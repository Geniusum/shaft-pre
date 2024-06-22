import colorama
from colorama import Fore
from colorama import Back

colorama.init()

class Errors():
    def __init__(self):
        self.t1 = {
            "bad": ["Bad", Fore.RED],
            "use_other": ["Use Other", Fore.YELLOW],
            "not_exists" :["Not Exists", Fore.RED]
        }
        self.t2 = {
            "syntax": "Syntax"
        }

    def colorInit(self):
        colorama.init()

    def getError(self, line:str, line_nb:int, file_path:str, t1:str="bad", t2:str="syntax"):
        return (Fore.RED +
                f"Code exception line {line_nb + 1} : " +
                self.t1[t1][1] +
                f"{self.t1[t1][0]} " +
                Fore.LIGHTYELLOW_EX +
                f"{self.t2[t2]}\n" +
                "  " +
                Back.RED +
                Fore.WHITE +
                f"{line}\n" +
                Fore.LIGHTYELLOW_EX +
                Back.RESET + f"File : {file_path}" +
                Back.RESET +
                Fore.RESET)

    def getErrorInter(self, file_path:str, t1:int=-1, t2:int=-1):
        return (Fore.RED +
                f"Interpreter exception : " +
                self.t1[t1][1] +
                f"{self.t1[t1][0]} " +
                Fore.LIGHTYELLOW_EX +
                f"{self.t2[t2]}\n" +
                Back.RESET + f"File : {file_path}" +
                Back.RESET +
                Fore.RESET)

ins = Errors()
print(ins.getError("var da =", 45, "main.sft", "bad", "syntax"))