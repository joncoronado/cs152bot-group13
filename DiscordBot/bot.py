# bot.py
import asyncio
import discord
from strike_handling import *
from discord.ext import commands
import os
import json
import logging
import re
import requests
from report import Report
import pdb
from automation import classify_message
from deep_translator import GoogleTranslator, single_detection

# Set up logging to the console
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

translator = GoogleTranslator(source='auto', target='en')

MOD_CHANNEL_ID = 1356427907035041953
context_path = 'context.json'

# There should be a file called 'tokens.json' inside the same folder as this file
token_path = 'tokens.json'
if not os.path.isfile(token_path):
    raise Exception(f"{token_path} not found!")
with open(token_path) as f:
    # If you get an error here, it means your token is formatted incorrectly. Did you put it in quotes?
    tokens = json.load(f)
    discord_token = tokens['discord']
    translator_token = tokens['detectlanguage']


class ModBot(discord.Client):
    def __init__(self): 
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='.', intents=intents)
        self.group_num = None
        self.mod_channels = {} # Map from guild to the mod channel id for that guild
        self.reports = {} # Map from user IDs to the state of their report
        self.strikes = load_strikes() # Map from user IDs to the number of strikes they have

    async def recommend_action(self, num_strikes):
        """
        Recommend an action based on the number of strikes.
        """
        recommendation, dm = "", ""
        if num_strikes <= 3:
            recommendation += "A warning should have been issued."
            dm += "Your post has been taken down and your account is under review. "
        # freeze account for 72hrs
        elif num_strikes == 4:
            recommendation += "The account should be frozen for 72 hours."
            dm += "Your account has been frozen for 72 hours. "
        # freeze account for 1 week
        elif num_strikes == 5:
            recommendation += "The account should be frozen for 1 week."
            dm += "Your account has been frozen for 1 week. "
        # freeze account for 30 days
        elif num_strikes == 6:
            recommendation += "The account should be frozen for 30 days."
            dm += "Your account has been frozen for 30 days. "
        # freeze account indefinitely
        elif num_strikes == 7:
            recommendation += "The account should be frozen indefinitely."
            dm += "Your account has been frozen indefinitely. "
        dm += "**Further strikes will have more severe consequences.**"

        return recommendation, dm
        
    async def get_and_update_strikes(self, user_id):
        if user_id in self.strikes['user_id'].values:
            self.strikes.loc[self.strikes['user_id'] == user_id, 'num_strikes'] += 1
        else:
            new_row = {'user_id': user_id, 'num_strikes': 1}
            self.strikes = pd.concat([self.strikes, pd.DataFrame([new_row])], ignore_index=True)

        save_strikes(self.strikes)
        return self.strikes.loc[self.strikes['user_id'] == user_id, 'num_strikes'].iloc[0]
    
    async def handle_strikes(self, message):
        user_id = message.author.name
        num_strikes = await self.get_and_update_strikes(user_id)
        reply = f"This is strike {num_strikes} for user {user_id}. "

        user_dm = message.author
        dm = f"You have received a strike the following message which violates our community guidelines:\n\n *{message.content}*\n\n This is strike {num_strikes}. "

        recommendation, user_message = await self.recommend_action(num_strikes)

        reply += recommendation
        dm += user_message
        await asyncio.sleep(1)
        await user_dm.send(dm)
        return reply

    async def on_ready(self):
        print(f'{self.user.name} has connected to Discord! It is these guilds:')
        for guild in self.guilds:
            print(f' - {guild.name}')
        print('Press Ctrl-C to quit.')

        # Parse the group number out of the bot's name
        match = re.search('[gG]roup (\d+) [bB]ot', self.user.name)
        if match:
            self.group_num = match.group(1)
        else:
            raise Exception("Group number not found in bot's name. Name format should be \"Group # Bot\".")

        # Find the mod channel in each guild that this bot should report to
        for guild in self.guilds:
            for channel in guild.text_channels:
                if channel.name == f'group-{self.group_num}-mod':
                    self.mod_channels[guild.id] = channel
        

    async def on_message(self, message):
        '''
        This function is called whenever a message is sent in a channel that the bot can see (including DMs). 
        Currently the bot is configured to only handle messages that are sent over DMs or in your group's "group-#" channel. 
        '''
        # Ignore messages from the bot 
        if message.author.id == self.user.id:
            return

        # Check if this message was sent in a server ("guild") or if it's a DM
        if message.guild:
            await self.handle_channel_message(message)
        else:
            await self.handle_dm(message)

    async def handle_dm(self, message):
        # Handle a help message
        if message.content == Report.HELP_KEYWORD:
            reply =  "Use the `report` command to begin the reporting process.\n"
            reply += "Use the `cancel` command to cancel the report process.\n"
            await asyncio.sleep(1) 
            await message.channel.send(reply)
            return

        author_id = message.author.id
        responses = []

        # Only respond to messages if they're part of a reporting flow
        if author_id not in self.reports and not message.content.startswith(Report.START_KEYWORD):
            return

        # If we don't currently have an active report for this user, add one
        if author_id not in self.reports:
            self.reports[author_id] = Report(self)

        # Let the report class handle this message; forward all the messages it returns to us
        responses = await self.reports[author_id].handle_message(message)
        for r in responses:
            await asyncio.sleep(1)
            await message.channel.send(r)

        # If the report is complete or cancelled, remove it from our map
        # AND send to moderator channel
        if self.reports[author_id].report_complete():
            r = self.reports.pop(author_id)
            if r.type:
                mod_message = f"Report from **{message.author.name}:**\n\n{r.pretty_print()}"
                mod_message += "\n\nModeration guidelines:\n"
                mod_message += self.get_moderation_guidelines() + "\n"
                mod_message += await self.handle_strikes(r.message)

                mod_channel = self.mod_channels[MOD_CHANNEL_ID]
                await asyncio.sleep(1)
                await mod_channel.send(mod_message)


    async def get_context(self):
        with open(context_path) as context_file:
            context = json.load(context_file)
        return context

    async def add_message_to_context(self, message, context):
        new_message = {
            "user": message.author.name,
            "message": message.content,
            "timestamp": message.created_at.isoformat()
        }
        context.append(new_message)

        with open(context_path, 'w') as context_file:
            json.dump(context, context_file, indent=4)

    async def handle_channel_message(self, message):
        # Only handle messages sent in the "group-#" channel
        if not message.channel.name == f'group-{self.group_num}':
            return
        
        context = await self.get_context()

        if single_detection(message.content, api_key=translator_token) != 'en':
            message.content = translator.translate(message.content)

        await self.add_message_to_context(message, context)
        
        classification = classify_message(message.content, context)
        
        mod_channel = self.mod_channels[message.guild.id]

        if classification.harassment:
            forwarded_message = f'**Forwarded message:\n{message.author.name}:** *{message.content}*\n\n'
            forwarded_message += '**Analysis:**\n'
            forwarded_message += f'* **Harassment:** 🚨🚨{classification.harassment}🚨🚨\n'
            forwarded_message += '* **Tags:** ' + ', '.join(classification.tags) + '\n'
            forwarded_message += f'* **Reasoning:** {classification.reasoning}\n'
            forwarded_message += '* **Recommendation:** '
            forwarded_message += await self.handle_strikes(message)
            forwarded_message += '\n\n**Moderation guidelines:**\n' + self.get_moderation_guidelines()
            await asyncio.sleep(1)
            await mod_channel.send(forwarded_message)
        else:
            forwarded_message = f'**Forwarded message:\n{message.author.name}:** *{message.content}*\n\n'
            forwarded_message += '**Analysis:**\n'
            forwarded_message += f'* **Harassment:** {classification.harassment}\n'
            forwarded_message += f'* **Reasoning:** {classification.reasoning}\n'
            await asyncio.sleep(1)
            await mod_channel.send(forwarded_message)
        return

    def get_moderation_guidelines(self):
        reply = "1) Report **tangible violent threats** to authorities.\n"
        reply += "2) Report **doxxing** to authorities.\n"
        reply += "3) Report **blackmail, extortion, etc** to authorities at **moderator discretion.**\n"
        return reply

    
    def eval_text(self, message):
        ''''
        TODO: Once you know how you want to evaluate messages in your channel, 
        insert your code here! This will primarily be used in Milestone 3. 
        '''
        return message

    
    def code_format(self, text):
        ''''
        TODO: Once you know how you want to show that a message has been 
        evaluated, insert your code here for formatting the string to be 
        shown in the mod channel. 
        '''
        return "Evaluated: '" + text + "'"


client = ModBot()
client.run(discord_token)