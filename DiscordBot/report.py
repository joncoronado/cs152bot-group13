from enum import Enum, auto
from datetime import datetime
import discord
import re

class HarassmentReport(Enum):
    PHYSICAL_THREAT = auto()
    HATE_SPEECH = auto()
    POLITICALLY_MOTIVATED = auto()
    BULLYING = auto()
    OTHER = auto()

    def to_string(self):
        if self == HarassmentReport.PHYSICAL_THREAT:
            return "Physical Threat"
        elif self == HarassmentReport.HATE_SPEECH:
            return "Hate Speech"
        elif self == HarassmentReport.POLITICALLY_MOTIVATED:
            return "Politically Motivated"
        elif self == HarassmentReport.BULLYING:
            return "Bullying"
        elif self == HarassmentReport.OTHER:
            return "Other"

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
        self.detail = ""
        self.type = None
        self.opened = None
        self.message_link = None
    
    def get_harassment_type(self):
        '''
        This function lists the options to the user for kinds of harassment to report.
        '''
        reply = "Please select the type of harassment you would like to report:\n\n"
        reply += "1) Physical Threat\n"
        reply += "2) Hate Speech\n"
        reply += "3) Politically Motivated\n"
        reply += "4) Bullying\n"
        reply += "5) Other\n\n"
        reply += "Or say `cancel` to cancel the report."
        return reply
    
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
            self.opened = datetime.now()
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
                self.message_link = message.content
                message = await channel.fetch_message(int(m.group(3)))
                self.message = message
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
                reply = "Thank you for reporting this message. "
                return [reply + self.get_harassment_type()]
        
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
                    reply = "I'm sorry, I couldn't understand that. "
                    return [reply + self.get_harassment_type()]
            self.state = State.GET_DETAIL
            reply = f"You have selected {self.type.to_string()}. "
            reply += "If you would like, please reply with any additional details you would like to provide. "
            reply += "You can also say `done` to finish the report."
            return [reply]
        
        if self.state == State.REPORT_OTHER:
            self.detail += message.content + "\n"
            self.state = State.GET_DETAIL
            reply = "Thank you for your report. "
            reply += "If you would like, please reply with any additional details you would like to provide. "
            reply += "You can also say `done` to finish the report."
            return [reply]
        
        if self.state == State.GET_DETAIL:
            if message.content == self.COMPLETE_KEYWORD:
                self.state = State.REPORT_COMPLETE
                return ["Thank you for your report! It has been submitted."]
            else:
                self.detail += message.content
                self.state = State.REPORT_COMPLETE
                return ["Thank you for your report! It has been submitted."]

        return []

    def report_complete(self):
        return self.state == State.REPORT_COMPLETE
    
    def pretty_print(self):
        """
        Formats the report details into a user-friendly string.
        """
        report = "=== Report Summary ===\n"
        if self.opened:
            report += f"Report Opened: {self.opened.strftime('%Y-%m-%d %H:%M:%S')}\n"
        if self.message:
            report += f"Reported Message: {self.message.author.name}: {self.message.content}\n"
        if self.message_link:
            report += f"Message Link: {self.message_link}\n"
        if self.type:
            report += f"Harassment Type: {self.type.to_string()}\n"
        if self.detail.strip():
            report += f"Additional Details: {self.detail.strip()}\n"
        else:
            report += "Additional Details: None\n"
        report += "======================"
        return report
    


    

