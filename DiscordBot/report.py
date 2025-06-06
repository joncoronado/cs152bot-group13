from datetime import datetime
from enums import State, ReportType, HarassmentReport, Tags
import discord
import re

class Report:
    START_KEYWORD = "report"
    CANCEL_KEYWORD = "cancel"
    HELP_KEYWORD = "help"
    OTHER_KEYWORD = "other"
    COMPLETE_KEYWORD = "done"

    def __init__(self, client):
        self.state = State.REPORT_START # State
        self.client = client
        self.message = None
        self.detail = ""
        self.type = None                # ReportType
        self.opened = None
        self.message_link = None
        self.tags = []                  # List of Tags

    def get_block_answer(self):
        reply = "Would you like to block this user?\n\n"
        reply += "1) Yes\n"
        reply += "2) No\n"
        return reply
    
    def get_report_type(self):
        '''
        This function lists the options to the user for kinds of reports to make.
        '''
        reply = "Please select your reason for filing a report:\n\n"
        reply += "1) Harassment\n"
        reply += "2) Phishing\n"
        reply += "3) IT Problems\n"
        reply += "4) Inappopriate Content\n"
        reply += "5) Unknown Member\n\n"
        reply += "Or say `cancel` to cancel the report."
        return reply
    
    def get_hate_speech_type(self):
        '''
        This function lists the options to the user for kinds of hate speech to report.
        '''
        reply = "Please select from the following options:\n\n"
        reply += "1) Racism\n"
        reply += "2) Sexism\n"
        reply += "3) Homophobia\n"
        reply += "4) Transphobia\n"
        reply += "5) Religion\n"
        reply += "6) Ethnic/Cultural Groups\n"
        reply += "7) Other\n\n"
        return reply
    
    def get_harassment_type(self):
        '''
        This function lists the options to the user for kinds of harassment to report.
        '''
        reply = "Please select the type of harassment you would like to report:\n\n"
        reply += "1) Threat\n"
        reply += "2) Hate Speech\n"
        reply += "3) Bullying\n"
        reply += "4) Sexual Harassment\n"
        reply += "5) Other\n\n"
        reply += "Or say `cancel` to cancel the report."
        return reply
    
    async def handle_message(self, message):
        '''
        This function makes up the meat of the user-side reporting flow. It defines how we transition between states and what 
        prompts to offer at each of those states. You're welcome to change anything you want; this skeleton is just here to
        get you started and give you a model for working with Discord. 
        '''
        #############################################################################
        #############################################################################
        #############################################################################
        if message.content == self.CANCEL_KEYWORD:
            self.state = State.REPORT_COMPLETE
            return ["Report cancelled."]
        #############################################################################
        #############################################################################
        #############################################################################
        # User starts report, get messsage link
        if self.state == State.REPORT_START:
            reply =  "Thank you for starting the reporting process. "
            reply += "Say `help` at any time for more information.\n\n"
            reply += "Please copy paste the link to the message you want to report.\n"
            reply += "You can obtain this link by right-clicking the message and clicking `Copy Message Link`."
            self.state = State.AWAITING_MESSAGE
            self.opened = datetime.now()
            return [reply]
        #############################################################################
        #############################################################################
        #############################################################################
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
            reply = "I found this message:"
            reply += "```" + message.author.name + ": " + message.content + "```"
            reply += "\n" + self.get_report_type()
            return [reply]
        #############################################################################
        #############################################################################
        #############################################################################
        # Message has been identified, ask for type of report
        if self.state == State.MESSAGE_IDENTIFIED:
            match message.content:
                case "1":
                    self.type = ReportType.HARASSMENT
                    self.state = State.REPORT_HARASSMENT
                case "2":
                    self.type = ReportType.PHISHING
                    self.state = State.REPORT_OTHER
                case "3":
                    self.type = ReportType.IT_PROBLEMS
                    self.state = State.REPORT_OTHER
                case "4":
                    self.type = ReportType.INAPPROPRIATE_CONTENT
                    self.state = State.REPORT_OTHER
                case "5":
                    self.type = ReportType.UNKNOWN_MEMBER
                    self.state = State.REPORT_OTHER
                case _:
                    reply = "I'm sorry, I couldn't understand that. "
                    return [reply + self.get_report_type()]
            reply = f"You have selected {str(self.type)}. "
            # Get type of harassment
            if self.type == ReportType.HARASSMENT:
                reply += self.get_harassment_type()
                return [reply]
            else:
                reply += "If you would like, please reply with any additional details you would like to provide. "
                reply += "You can also say `done` to finish the report."
        #############################################################################
        #############################################################################
        #############################################################################
        # Getting harassment type
        if self.state == State.REPORT_HARASSMENT:
            match message.content:
                case "1":
                    self.type = HarassmentReport.THREAT
                    self.tags.append(Tags.THREAT)
                case "2":
                    self.type = HarassmentReport.HATE_SPEECH
                    self.tags.append(Tags.HATE_SPEECH)
                case "3":
                    self.type = HarassmentReport.BULLYING
                    self.tags.append(Tags.BULLYING)
                case "4":
                    self.type = HarassmentReport.SEXUAL_HARASSMENT
                    self.tags.append(Tags.SEXUAL_HARASSMENT)
                case "5":
                    self.type = HarassmentReport.OTHER
                    self.tags.append(Tags.OTHER)
                case _:
                    reply = "I'm sorry, I couldn't understand that. "
                    return [reply + self.get_harassment_type()]
            reply = f"You have selected {str(self.type.to_string())}. "
        #############################################################################
        #############################################################################
        #############################################################################
        # Handling harassment reports

        # threats
        if self.state == State.REPORT_HARASSMENT and self.type == HarassmentReport.THREAT:
            self.state = State.HARASSMENT_THREAT
            reply = "Who was the threat directed at? Please select from the following options:\n\n"
            reply += "1) Myself\n"
            reply += "2) Loved ones\n"
            reply += "3) Other\n\n"
            return [reply]

        # hate speech
        if self.state == State.REPORT_HARASSMENT and self.type == HarassmentReport.HATE_SPEECH:
            self.state = State.HARASSMENT_HATE_SPEECH
            reply = "How would you like to classify this hate speech? "
            reply = self.get_hate_speech_type()
            return [reply]
        
        # SA
        if self.state == State.REPORT_HARASSMENT and self.type == HarassmentReport.SEXUAL_HARASSMENT:
            self.state = State.GET_BLOCK
            reply = "We are sorry to hear that you are experiencing this. Your message has been flagged for review. "
            reply += self.get_block_answer()
            return [reply]

        # bullying, other
        if self.state == State.REPORT_HARASSMENT and (self.type == HarassmentReport.BULLYING or self.type == HarassmentReport.OTHER):
            self.state = State.GET_DETAIL
            reply = "Thank you for your report. "
            reply += "If you would like, please reply with any additional details you would like to provide. "
            reply += "You can also say `done` to finish the report."
            return [reply]
        #############################################################################
        #############################################################################
        #############################################################################
        # check if user wants to block
        if self.state == State.GET_BLOCK:
            match message.content:
                case "1":
                    # say that user has been blocked
                    self.tags.append(Tags.BLOCKED)
                    reply = "The user has been blocked. Your report has been filed and will be reviewed shortly. "
                    self.state  = State.REPORT_COMPLETE
                    return [reply]
                case "2":
                    # say that user has not been blocked
                    self.tags.append(Tags.NOT_BLOCKED)
                    reply = "The user has not been blocked. Your report has been filed and will be reviewed shortly. "
                    self.state = State.REPORT_COMPLETE
                    return [reply]
                case _:
                    reply = "I'm sorry, I couldn't understand that. "
                    return [reply + self.get_block_answer()]
                
        #############################################################################
        #############################################################################
        #############################################################################

        # classify hate speech
        if self.state == State.HARASSMENT_HATE_SPEECH:
            match message.content:
                case "1":
                     self.tags.append(Tags.RACISM)
                case "2":
                    self.tags.append(Tags.SEXISM)
                case "3":
                    self.tags.append(Tags.HOMOPHOBIA)
                case "4":
                    self.tags.append(Tags.TRANSPHOBIA)
                case "5":
                    self.tags.append(Tags.RELIGIOUS_DISCRIMINATION)
                case "6":
                    self.tags.append(Tags.ETHNIC_CULTURAL_DISCRIMINATION)
                case "7":
                    self.tags.append(Tags.OTHER)
                case _:
                    reply = "I'm sorry, I couldn't understand that. "
                    return [reply + self.get_hate_speech_type()]
            self.state = State.GET_DETAIL
            reply = "Thank you for your report. "
            reply += "If you would like, please reply with any additional details you would like to provide. "
            reply += "You can also say `done` to finish the report."
            return [reply]

        #############################################################################
        #############################################################################
        #############################################################################
        # who was threat directed at?
        if self.state == State.HARASSMENT_THREAT:
            match message.content:
                case "1":
                    self.tags.append(Tags.PERSONAL_THREAT)
                case "2":
                    self.tags.append(Tags.LOVED_ONES_THREAT)
                case "3":
                    self.tags.append(Tags.OTHER_THREAT)
                case _:
                    reply = "I'm sorry, I couldn't understand that. "
                    return [reply + self.get_harassment_type()]
            self.state = State.GET_VIOLENT
            reply = "We are sorry to hear that you are experiencing this. Was this threat violent in nature?\n\n"
            reply += "1) Yes\n"
            reply += "2) No\n"
            return [reply]
        
        # check if threat was violent
        if self.state == State.GET_VIOLENT:
            match message.content:
                # violent threat ends report
                case "1":
                    self.tags.append(Tags.VIOLENT)
                    self.state = State.GET_DETAIL
                    reply = "Thank you for your report. "
                    reply += "If you would like, please reply with any additional details you would like to provide. "
                    reply += "You can also say `done` to finish the report."
                    return [reply]
                case "2":
                    self.tags.append(Tags.NONVIOLENT)
                    self.state = State.HARASSMENT_NONVIOLENT_THREAT
                case _:
                    reply = "I'm sorry, I couldn't understand that. "
                    return [reply + self.get_harassment_type()]
                
        # non-violent threat
        if self.state == State.HARASSMENT_NONVIOLENT_THREAT:
            self.state = State.GET_NONVIOLENT_TYPE
            reply = "We are sorry to hear that you are experiencing this. How would you describe the nature of this threat?\n\n"
            reply += "1) Extortion\n"
            reply += "2) Blackmail\n"
            reply += "3) Doxxing\n"
            reply += "4) Other\n\n"
            return [reply]
        
        #############################################################################
        #############################################################################
        #############################################################################
        # Classify non-violent threat
        if self.state == State.GET_NONVIOLENT_TYPE:
            match message.content:
                case "1":
                    self.tags.append(Tags.EXTORTION)
                case "2":
                    self.tags.append(Tags.BLACKMAIL)
                case "3":
                    self.tags.append(Tags.DOXXING)
                case "4":
                    self.tags.append(Tags.OTHER)
                case _:
                    reply = "I'm sorry, I couldn't understand that. "
                    return [reply + self.get_harassment_type()]
            self.state = State.GET_DETAIL
            reply = "Thank you for your report. "
            reply += "If you would like, please reply with any additional details you would like to provide. "
            reply += "You can also say `done` to finish the report."
            return [reply]


        #############################################################################
        #############################################################################
        #############################################################################
        # Handling other reports (not harassment)
        
        if self.state == State.REPORT_OTHER:
            self.state = State.GET_DETAIL
            reply = "Your complaint has been filed! Thank you for your report. "
            return [reply]
        #############################################################################
        #############################################################################
        #############################################################################
        # Get details at end of report

        if self.state == State.GET_DETAIL:
            if message.content != self.COMPLETE_KEYWORD:
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
        if self.message:
            report += f"**Reported User:** {self.message.author.name}\n"
            report += f"**Reported Message:** *{self.message.content}*\n"
        if self.message_link:
            report += f"**Message Link:** {self.message_link}\n"
        if self.opened:
            report += f"**Report Opened:** {self.opened.strftime('%Y-%m-%d %H:%M:%S')}\n"
        if self.type:
            report += f"**Harassment Type:** {str(self.type)}\n"
        if self.detail.strip():
            report += f"**Additional Details:** {self.detail.strip()}\n"
        if self.tags:
            report += "**Tags:** " + ", ".join(str(tag) for tag in self.tags) + "\n"
        else:
            report += "Additional Details: None\n"
        report += "======================"
        return report
    


    

