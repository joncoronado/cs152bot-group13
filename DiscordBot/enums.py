from enum import Enum, auto

class ReportType(Enum):
    HARASSMENT = auto()
    PHISHING = auto()
    IT_PROBLEMS = auto()
    INAPPROPRIATE_CONTENT = auto()
    UNKNOWN_MEMBER = auto()

    def to_string(self):
        if self == ReportType.HARASSMENT:
            return "Harassment"
        elif self == ReportType.PHISHING:
            return "Phishing"
        elif self == ReportType.IT_PROBLEMS:
            return "IT Problems"
        elif self == ReportType.INAPPROPRIATE_CONTENT:
            return "Inappropriate Content"
        elif self == ReportType.UNKNOWN_MEMBER:
            return "Unknown Member"

class HarassmentReport(Enum):
    THREAT = auto()
    HATE_SPEECH = auto()
    SEXUAL_HARASSMENT = auto()
    BULLYING = auto()
    OTHER = auto()

    def to_string(self):
        if self == HarassmentReport.THREAT:
            return "Threat"
        elif self == HarassmentReport.HATE_SPEECH:
            return "Hate Speech"
        elif self == HarassmentReport.SEXUAL_HARASSMENT:
            return "Sexual Harassment"
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
    HARASSMENT_THREAT = auto()
    HARASSMENT_HATE_SPEECH = auto()
    HARASSMENT_VIOLENT_THREAT = auto()
    HARASSMENT_NONVIOLENT_THREAT = auto()
    GET_VIOLENT = auto()
    GET_NONVIOLENT_TYPE = auto()
    GET_BLOCK = auto()

class Tags(Enum):
    HARASSMENT = auto()
    PHISHING = auto()
    IT_PROBLEMS = auto()
    INAPPROPRIATE_CONTENT = auto()
    UNKNOWN_MEMBER = auto()
    THREAT = auto()
    HATE_SPEECH = auto()
    SEXUAL_HARASSMENT = auto()
    BULLYING = auto()
    VIOLENT = auto()
    NONVIOLENT = auto()
    PERSONAL_THREAT = auto()
    LOVED_ONES_THREAT = auto()
    OTHER_THREAT = auto()
    EXTORTION = auto()
    BLACKMAIL = auto()
    DOXXING = auto()
    RACISM = auto()
    SEXISM = auto()
    HOMOPHOBIA = auto()
    TRANSPHOBIA = auto()
    RELIGIOUS_DISCRIMINATION = auto()
    ETHNIC_CULTURAL_DISCRIMINATION = auto()
    BLOCKED = auto()
    NOT_BLOCKED = auto()
    OTHER = auto()

    def to_string(self):
        if self == Tags.HARASSMENT:
            return "Harassment"
        elif self == Tags.PHISHING:
            return "Phishing"
        elif self == Tags.IT_PROBLEMS:
            return "IT Problems"
        elif self == Tags.INAPPROPRIATE_CONTENT:
            return "Inappropriate Content"
        elif self == Tags.UNKNOWN_MEMBER:
            return "Unknown Member"
        elif self == Tags.THREAT:
            return "Threat"
        elif self == Tags.HATE_SPEECH:
            return "Hate Speech"
        elif self == Tags.SEXUAL_HARASSMENT:
            return "Sexual Harassment"
        elif self == Tags.BULLYING:
            return "Bullying"
        elif self == Tags.VIOLENT:
            return "Violent Threat"
        elif self == Tags.NONVIOLENT:
            return "Nonviolent Threat"
        elif self == Tags.PERSONAL_THREAT:
            return "Personal Threat"
        elif self == Tags.LOVED_ONES_THREAT:
            return "Loved Ones Threat"
        elif self == Tags.OTHER_THREAT:
            return "Other Threat"
        elif self == Tags.EXTORTION:
            return "Extortion"
        elif self == Tags.BLACKMAIL:
            return "Blackmail"
        elif self == Tags.DOXXING:
            return "Doxxing"
        elif self == Tags.RACISM:
            return "Racism"
        elif self == Tags.SEXISM:
            return "Sexism"
        elif self == Tags.HOMOPHOBIA:
            return "Homophobia"
        elif self == Tags.TRANSPHOBIA:
            return "Transphobia"
        elif self == Tags.RELIGIOUS_DISCRIMINATION:
            return "Religious Discrimination"
        elif self == Tags.ETHNIC_CULTURAL_DISCRIMINATION:
            return "Ethnic/Cultural Discrimination"
        elif self == Tags.BLOCKED:
            return "Blocked"
        elif self == Tags.NOT_BLOCKED:
            return "Not Blocked"
        elif self == Tags.OTHER:
            return "Other"
        else:
            return "Unknown"

