class Student:
    """ This is a class for students of Golestan website. 
    their name, credential and public data are here. """

    def __init__(self, firstName, lastName, studentNumber) -> None:
        self.firstName = firstName
        self.lastName = lastName
        self.studentNumber = studentNumber
    
    def __str__(self) -> str:
        return self.firstName + " " + self.lastName

    # @property
    # def firstName(self):
    #     return self.firstName

    # @firstName.setter
    # def firstName(self, value):
    #     self.firstName = value

    # @firstName.getter
    # def firstName(self):
    #     return self.firstName

    # @property
    # def lastName(self):
    #     return self.lastName

    # @lastName.setter
    # def lastName(self, value):
    #     self.lastName = value
    

ehsan = Student('Ehsan', 'Attar', '94432027')
# ehsan.firstName('Ehsan')
# ehsan.lastName('Attar')
print(ehsan)
