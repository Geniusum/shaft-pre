from src.libs.errors import *
from src.libs.valuetypes import *

class ShaftValue():
    def __new__(self, type_:str, value:list):
        self.types = ShaftValueTypes()
        self.type = type_
        self.value = value
        if type(value) != list:
            value = [value]
        
        if not self.type in self.types.keys():
            ShaftError("Unknown type")
        
        if self.type in self.types["integer"]:
            try:
                self.value = [int(self.value)]
            except:
                ShaftError("Not a valid integer")
        elif self.type in self.types["string"]:
            try:
                self.value = [str(self.value)]
            except:
                ShaftError("Not a valid string")
        elif self.type in self.types["decimal"]:
            try:
                self.value = [float(self.value)]
            except:
                ShaftError("Not a valid decimal")
        elif self.type in self.types["array"]:
            try:
                self.value = [list()]  # Initialize an empty list
            except:
                ShaftError("Failed to initialize array")

        return self.value