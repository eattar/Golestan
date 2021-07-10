from dataclasses import dataclass

@dataclass
class Student:
    """ This is a dataclass for students of Golestan website. 
    Their educational and public data are stored here. """

    university: str
    faculty: str
    department: str
    subject: str
    degree: str
    courseType: str