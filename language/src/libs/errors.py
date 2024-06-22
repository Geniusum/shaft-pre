class ShaftError():
    def __init__(self, message:str, line:int=-1) -> None:
        print(f"Error line {line} : {message}")
        exit()