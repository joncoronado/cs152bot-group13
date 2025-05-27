# bot.py
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

# Set up logging to the console
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

MOD_CHANNEL_ID = 1356427907035041953

# There should be a file called 'tokens.json' inside the same folder as this file
token_path = 'tokens.json'
if not os.path.isfile(token_path):
    raise Exception(f"{token_path} not found!")
with open(token_path) as f:
    # If you get an error here, it means your token is formatted incorrectly. Did you put it in quotes?
    tokens = json.load(f)
    discord_token = tokens['discord']


class ModBot(discord.Client):
    def __init__(self): 
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='.', intents=intents)
        self.group_num = None
        self.mod_channels = {} # Map from guild to the mod channel id for that guild
        self.reports = {} # Map from user IDs to the state of their report
        self.strikes = load_strikes() # Map from user IDs to the number of strikes they have
    
    async def handle_strikes(self, report):
        user_id = report.message.author.name

        if user_id in self.strikes['user_id'].values:
            self.strikes.loc[self.strikes['user_id'] == user_id, 'num_strikes'] += 1
        else:
            new_row = {'user_id': user_id, 'num_strikes': 1}
            self.strikes = pd.concat([self.strikes, pd.DataFrame([new_row])], ignore_index=True)

        save_strikes(self.strikes)
        num_strikes = self.strikes.loc[self.strikes['user_id'] == user_id, 'num_strikes'].iloc[0]
        reply = f"This is strike {num_strikes} for user {user_id}. "

        user_dm = report.message.author
        dm = f"You have received a strike the following message which violates our community guidelines:\n\n *{report.message.content}*\n\n This is strike {num_strikes}. "

        # warning
        if num_strikes < 3:
            reply += "A warning has been issued."
        # take down post, notify user that they are under review
        elif num_strikes == 3:
            reply += "The post should be taken down and the user will be notified that they are under review."
            dm += "Your post has been taken down and your account is under review. "
        # freeze account for 72hrs
        elif num_strikes == 4:
            reply += "The account should be frozen for 72 hours."
            dm += "Your account has been frozen for 72 hours. "
        # freeze account for 1 week
        elif num_strikes == 5:
            reply += "The account should be frozen for 1 week."
            dm += "Your account has been frozen for 1 week. "
        # freeze account for 30 days
        elif num_strikes == 6:
            reply += "The account should be frozen for 30 days."
            dm += "Your account has been frozen for 30 days. "
        # freeze account indefinitely
        elif num_strikes == 7:
            reply += "The account should be frozen indefinitely."
            dm += "Your account has been frozen indefinitely. "

        dm += "**Further strikes will have more severe consequences.**"
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
            await message.channel.send(r)

        # If the report is complete or cancelled, remove it from our map
        # AND send to moderator channel
        if self.reports[author_id].report_complete():
            r = self.reports.pop(author_id)
            if r.type:
                mod_message = f"Report from **{message.author.name}:**\n\n{r.pretty_print()}"
                mod_message += "\n\nModeration guidelines:\n"
                mod_message += self.get_moderation_guidelines() + "\n"
                mod_message += await self.handle_strikes(r)

                mod_channel = self.mod_channels[MOD_CHANNEL_ID]
                await mod_channel.send(mod_message)

    async def handle_channel_message(self, message):
        # Only handle messages sent in the "group-#" channel
        # if not message.channel.name == f'group-{self.group_num}':
        #     return

        # # Forward the message to the mod channel
        # # TODO: Add some sort of check to only send messages that are relevant to the mod channel
        classification = classify_message(message.content)
        
        mod_channel = self.mod_channels[message.guild.id]
        forwarded_message = f'**Forwarded message:\n{message.author.name}:** *{message.content}*\n\n'
        forwarded_message += f'**Classification:** {classification}'
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
        return "Evaluated: '" + text+ "'"


client = ModBot()
client.run(discord_token)