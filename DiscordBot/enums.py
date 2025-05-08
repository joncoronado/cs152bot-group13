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

