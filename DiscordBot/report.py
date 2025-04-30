from enum import Enum, auto
import discord
import re

class HarassmentReport(Enum):
    PHYSICAL_THREAT = auto()
    HATE_SPEECH = auto()
    POLITICALLY_MOTIVATED = auto()
    BULLYING = auto()
    OTHER = auto()

class State(Enum):
    REPORT_START = auto()
    AWAITING_MESSAGE = auto()
    MESSAGE_IDENTIFIED = auto()
    REPORT_COMPLETE = auto()
    REPORT_OTHER = auto()
    REPORT_HARASSMENT = auto()
    GET_DETAIL = auto()

class Report:
    START_KEYWORD = "report"
    CANCEL_KEYWORD = "cancel"
    HELP_KEYWORD = "help"
    HARRASSMENT_KEYWORD = "harassment"
    OTHER_KEYWORD = "other"
    COMPLETE_KEYWORD = "done"

    def __init__(self, client):
        self.state = State.REPORT_START
        self.client = client
        self.message = None
        self.detail = None
        self.type = None
    
    async def get_harassment_type(self):
        reply = "Thank you for reporting this message. Please select the type of harassment you would like to report:\n"
        reply += "1. Physical threat\n"
        reply += "2. Hate Speech\n"
        reply += "3. Politically Motivated\n"
        reply += "4. Bullying\n"
        reply += "5. Other"
        return [reply]
    
    async def handle_message(self, message):
        '''
        This function makes up the meat of the user-side reporting flow. It defines how we transition between states and what 
        prompts to offer at each of those states. You're welcome to change anything you want; this skeleton is just here to
        get you started and give you a model for working with Discord. 
        '''

        if message.content == self.CANCEL_KEYWORD:
            self.state = State.REPORT_COMPLETE
            return ["Report cancelled."]
                
        if self.state == State.REPORT_START:
            reply =  "Thank you for starting the reporting process. "
            reply += "Say `help` at any time for more information.\n\n"
            reply += "Please copy paste the link to the message you want to report.\n"
            reply += "You can obtain this link by right-clicking the message and clicking `Copy Message Link`."
            self.state = State.AWAITING_MESSAGE
            return [reply]
        
        if self.state == State.AWAITING_MESSAGE:
            # Parse out the three ID strings from the message link
            m = re.search('/(\d+)/(\d+)/(\d+)', message.content)
            if not m:
                return ["I'm sorry, I couldn't read that link. Please try again or say `cancel` to cancel."]
            guild = self.client.get_guild(int(m.group(1)))
            if not guild:
                return ["I cannot accept reports of messages from guilds that I'm not in. Please have the guild owner add me to the guild and try again."]
            channel = guild.get_channel(int(m.group(2)))
            if not channel:
                return ["It seems this channel was deleted or never existed. Please try again or say `cancel` to cancel."]
            try:
                message = await channel.fetch_message(int(m.group(3)))
            except discord.errors.NotFound:
                return ["It seems this message was deleted or never existed. Please try again or say `cancel` to cancel."]

            # Here we've found the message - it's up to you to decide what to do next!
            self.state = State.MESSAGE_IDENTIFIED
            return ["I found this message:", "```" + message.author.name + ": " + message.content + "```", \
                    "What would you like to report this message for? Please say `harassment` or `other`."]
        
        if self.state == State.MESSAGE_IDENTIFIED:
            if message.content == self.OTHER_KEYWORD:
                self.state = State.REPORT_OTHER
                return ["Please describe the harassment in the message in your own words. You can also say `cancel` to cancel the report."]
            if message.content == self.HARRASSMENT_KEYWORD:
                self.state = State.REPORT_HARASSMENT
                return self.get_harassment_type(message)
        
        if self.state == State.REPORT_HARASSMENT:
            match message.content:
                case "1":
                    self.type = HarassmentReport.PHYSICAL_THREAT
                case "2":
                    self.type = HarassmentReport.HATE_SPEECH
                case "3":
                    self.type = HarassmentReport.POLITICALLY_MOTIVATED
                case "4":
                    self.type = HarassmentReport.BULLYING
                case "5":
                    self.type = HarassmentReport.OTHER
                case _:
                    reply = ["I'm sorry, I couldn't understand that. Please select one of the following harassment types:\n"]
                    reply += "1. Physical threat\n"
                    reply += "2. Hate Speech\n"
                    reply += "3. Politically Motivated\n"
                    reply += "4. Bullying\n"
                    reply += "5. Other"
                    return reply

        return []

    def report_complete(self):
        return self.state == State.REPORT_COMPLETE
    


    

