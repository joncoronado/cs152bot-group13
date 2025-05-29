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

class Tags(str, Enum):
    HARASSMENT = "Harassment"
    PHISHING = "Phishing"
    IT_PROBLEMS = "IT Problems"
    INAPPROPRIATE_CONTENT = "Inappropriate Content"
    UNKNOWN_MEMBER = "Unknown Member"
    THREAT = "Threat"
    HATE_SPEECH = "Hate Speech"
    SEXUAL_HARASSMENT = "Sexual Harassment"
    BULLYING = "Bullying"
    VIOLENT = "Violent Threat"
    NONVIOLENT = "Nonviolent Threat"
    PERSONAL_THREAT = "Personal Threat"
    LOVED_ONES_THREAT = "Loved Ones Threat"
    OTHER_THREAT = "Other Threat"
    EXTORTION = "Extortion"
    BLACKMAIL = "Blackmail"
    DOXXING = "Doxxing"
    RACISM = "Racism"
    SEXISM = "Sexism"
    HOMOPHOBIA = "Homophobia"
    TRANSPHOBIA = "Transphobia"
    RELIGIOUS_DISCRIMINATION = "Religious Discrimination"
    ETHNIC_CULTURAL_DISCRIMINATION = "Ethnic/Cultural Discrimination"
    BLOCKED = "Blocked"
    NOT_BLOCKED = "Not Blocked"
    OTHER = "Other"
