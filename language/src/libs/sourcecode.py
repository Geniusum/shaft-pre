from src.libs.exceptions import *

class SourceCode():
    def __init__(self, code:str) -> None:
        self.code = code

    def getLines(self) -> list:
        """
        Return a list with all code lines.
        """

        return self.code.splitlines()

    def getLinesLenght(self) -> int:
        """
        Return the length of code lines.
        """

        return len(self.getLine())

    def getLine(self, index:int) -> str:
        """
        Return the corresponding line, index start at 0.
        Raise an exception if can't reach the line.
        """

        if index > self.getLinesLenght() - 1:
            raise CannotReachLine(index)
        elif index < 0:
            raise BadValue(index)
        else:
            return str(self.getLines()[index])
    
    def searchLineIndex(self, line:str) -> int:
        """
        Research the first occurence of the line and return it index.
        """

        if len(line.splitlines()) > 1:
            raise MustBeALine(line)

        for line_index, line_comparing in enumerate(self.getLines()):
            if line_comparing.strip() == line.strip():
                return line_index
            
        return None
    
    def getPairLines(self) -> dict:
        """
        Create a dict of pair index/line.
        """

        paires = {}

        for line_index, line_content in enumerate(self.getLines()):
            paires[line_index] = line_content
        
        return paires

    def getPairLinesNb(self) -> dict:
        """
        Create a dict of pair number/line.
        """

        paires = {}

        for line_number, line_content in enumerate(self.getLines()):
            line_number += 1
            paires[line_number] = line_content
    
    def getPaireLinesList(self) -> list:
        """
        Create a list of pair number/line.
        """

        paires = []

        for line_index, line_content in enumerate(self.getLines()):
            paires.append([line_index, line_content])
        
        return paires