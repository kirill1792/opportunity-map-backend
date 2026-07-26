from enum import Enum


class OpportunityType(str, Enum):
    INTERNSHIP = "internship"
    HACKATHON = "hackathon"
    SCHOOL = "school"
    COMPETITION = "competition"
    EVENT = "event"
    COURSE = "course"


class OpportunityFormat(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    HYBRID = "hybrid"


class OpportunityLevel(str, Enum):
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    ANY = "any"