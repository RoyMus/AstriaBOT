from enum import Enum


class States(Enum):
    NEW = 0
    PICTURESLOADED = 1
    TUNEREADY = 2
    WRITING_FEEDBACK = 3    


class Languages(Enum):
    ENGLISH = 0
    HEBREW = 1