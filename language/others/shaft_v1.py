import re
import random as rd

class SourceCode():
    def __new__(self, code:str) -> list:
        self.nb_lines = len(code.splitlines())
        self.or_lines = code.splitlines()
        self.lines = []
        for i, line in enumerate(self.or_lines):
            line = line.strip()
            if len(line):
                self.lines.append([i + 1, line])
        return self.lines

    def lines(self) -> list:
        return self.lines
    
    def nb_lines(self) -> int:
        return self.nb_lines

    def or_lines(self) -> list:
        return self.or_lines

class ShaftValueTypes():
    def __new__(cls) -> dict: return {
            "integer": ["int", "integer"],
            "string": ["string", "str"],
            "array": ["list", "array"],
            "decimal": ["decimal", "float"],
            "boolean": ["bool", "boolean"]
        }
    
class ShaftError():
    def __init__(self, message:str, line:int=-1) -> None:
        print(f"Error line {line} : {message}")
        exit()

class ShaftValue():
    def __new__(self, type_:str, value:list):
        self.types = ShaftValueTypes()
        self.type = type_
        self.value = value
        if type(value) != list:
            value = [value]
        
        if not self.type in self.types.keys():
            ShaftError("Unknow type")
        
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
        elif self.type == self.types["decimal"]:
            try:
                self.value = [float(self.value)]
            except:
                ShaftError("Not a valid decimal")
        elif self.type == self.types["array"]:
            try:
                self.value = [list[]] # Continue here

class Shaft():
    def __init__(self) -> None:
        self.lexical = {
            "syn_operators": {
                "plus": ["+"],
                "minus": ["-"],
                "divide": ["/"],
                "mul": ["*"],
                "is_equal": ["==", "?="],
                "is_not_equal": ["!=", "?!="],
                "more_equal": [">="],
                "less_equal": ["<="],
                "more": [">"],
                "less": ["<"],
                "concat": ["&"],
                "power": ["^"],
                "bracket_open": ["("],
                "bracket_close": [")"]
            },
            "strings": {
                "string": ["\"", "'"],
                "backslash": ["\\\\"],
                "new_line": ["\\n"],
                "tab": ["\\t"],
                "db_quotes": ["\\\""],
                "quote": ["\\'"],
                "db_slash": ["\s"],
                "com_open": ["\so"],
                "com_close": ["\sc"],
                "semicolon": ["\sm"]
            },
            "comments": {
                "one_line": ["//"],
                "multi_lines_open": ["/*"],
                "multi_lines_close": ["*/"]
            }
        }

        self.numbers = [*"0123456789"]

        self.strings = {}

        self.scopes = {
            "global": {
                "0x0": {
                    "name_type": "variable",
                    "type": "list",
                    "values": []
                }
            }
        }

        self.flux = {}

    def getNewAddress(self, scope:str):
        if scope in self.scopes.keys():
            scope_dict = self.scopes[scope]
            active_addresses = scope_dict.keys()
            sel_addr = None
            act_addr = hex(0)
            if act_addr in active_addresses:
                while act_addr in active_addresses:
                    act_addr = hex(int(act_addr) + 1)
                sel_addr = act_addr
            else:
                sel_addr = act_addr

    def removeComments(self, code:SourceCode):
        lines_to_keep = []
        multi_lines = False
        
        for line_number, line in code:
            line = line.strip()
            current_line = ""
            if len(line) >= 2:
                if line[:2] in self.lexical["comments"]["one_line"]:
                    pass
                else:
                    for i, char in enumerate([*line]):
                        try: double = char + line[i + 1]
                        except: double = ""
                        if double in self.lexical["comments"]["multi_lines_open"]:
                            multi_lines = True
                        elif double in self.lexical["comments"]["multi_lines_close"]:
                            multi_lines = False
                        else:
                            if not multi_lines and char != "/":
                                current_line += char
            line = current_line.strip()
            if len(line):
                lines_to_keep.append([line_number, line])
        
        return lines_to_keep
    
    def genStringID(self):
        r = "#"
        for _ in range(16):
            r += rd.choice(self.numbers)
        if r in self.strings.keys():
            r = self.genStringID()
        return r
    
    def mkStringReference(self, string:str, id:str):
        self.strings[id] = string

    def refAllStrings(self, exp:str):
        ls = self.lexical["strings"]
        for i in ls["backslash"]:
            exp = exp.replace(i, "\\")
        for k, h in {"new_line": "\n", "tab": "\t", "db_quotes": "š", "quote": "ž", "db_slash": "//", "com_open": "/*", "com_close": "*/", "semicolon": "sm"}.items():
            for i in ls[k]:
                exp = exp.replace(i, h)
        string = False
        buffer = ""
        buffer2 = ""
        current_sep = ""
        strings = []
        for char in [*exp]:
            ex = char in ls["string"]
            if current_sep != "":
                ex = char == current_sep
            if ex:
                if string:
                    current_sep = ""
                    string = False
                    id = self.genStringID()
                    buffer = buffer.replace("š", "\"").replace("ž", "\'")
                    strings.append([buffer, id])
                    buffer = ""
                    buffer2 += id
                else:
                    string = True
                    current_sep = char
            else:
                if string:
                    buffer += char
                else:
                    buffer2 += char
        for string_ in strings:
            string = string_[0]
            id = string_[1]
            self.mkStringReference(string, id)
        return buffer2
    
    def getStringFromRefID(self, id:str):
        for string_id, string in self.strings.items():
            if id == string_id:
                return string

    def split_spec(self, exp:str):
        for k, ops in self.lexical["syn_operators"].items():
            for op in ops:
                exp = re.sub(r'(?<!\S)' + re.escape(op) + r'(?!\S)', ' ' + op + ' ', exp)

        exp = re.sub(r'(?<=\d|\))(?=[^\d\)])|(?<=[^\d\()])(?=\d|\()|(?<=\()(?=\d)|(?<=\d)(?=\))', ' ', exp)
        
        return " ".join(exp.split())
    
    def parse_code(self, code_wl:SourceCode):
        # WL : With lines
        self.flux = {
            "token": [],
            "instruction": None,
            "mode": None,
            "chars": [],
            "index": 0,
            "actual": ""
        }
        for _ in code_wl:
            line = _[0]
            code = _[1]
            for index, char in enumerate(code):
                self.flux["index"] = index
                self.flux["chars"].append(char)

                if char == ";" and self.flux["mode"] == None:
                    self.flux["instruction"] = None
                    self.flux["chars"] = ""
                    
                    break
                
                if char == ""

    def convertFloatToIntIfPossible(self, num):
        if isinstance(num, float):
            if num.is_integer():
                return int(num)
        return float(num)

    def parse(self, exp:str):
        exp = exp.strip()
        exp = self.refAllStrings(exp)
        tokens_ = self.split_spec(exp).split()
        string_id = None
        tokens = []
        for ind, token in enumerate(tokens_):
            if token == "#":
                try:
                    tokens.append(tokens_[ind] + tokens_[ind + 1])
                except:
                    tokens.append(token)
                tokens_.pop(ind + 1)
            else:
                tokens.append(token)
        parsed = []
        for token in tokens:
            type = "UNK"
            nb_type = ""
            op_type = ""
            if token[0] in self.numbers:
                type = "NB"
                nb_type = "INT"
                if "." in token:
                    nb_type = "DEC"
            if not type == "NB":
                if token[0] == "#":
                    token = self.getStringFromRefID(token)
                    type = "STR"
            for k, op in self.lexical["syn_operators"].items():
                for op_ in op:
                    if token == op_:
                        type = "OP"
                        op_type = k
            r = [token, type]
            if op_type != "":
                r.append(op_type)
            if nb_type != "":
                r.append(nb_type)
            parsed.append(r)
        parsed2 = []

        # Ici, utilise l'algorithme Shunting Yard pour convertir en notation postfixe
        precedence = {
            "mul": 2,
            "divide": 2,
            "power": 2,
            "is_equal": 2,
            "is_not_equal": 2,
            "more_equal": 2,
            "less_equal": 2,
            "more": 2,
            "less": 2,
            "concat": 2,
            "plus": 1,
            "minus": 1
        }

        stack = []
        for token in parsed:
            if token[1] == "NB":
                parsed2.append(token)
            elif token[1] == "STR":
                parsed2.append(token)
            elif token[1] == "OP":
                if token[2] == "bracket_open":
                    stack.append(token)
                elif token[2] == "bracket_close":
                    while stack and stack[-1][2] != "bracket_open":
                        parsed2.append(stack.pop())
                    if stack:
                        stack.pop()  # Dépiler la parenthèse ouvrante
                else:
                    while stack and precedence.get(stack[-1][2], 0) >= precedence.get(token[2], 0):
                        parsed2.append(stack.pop())
                    stack.append(token)
        while stack:
            parsed2.append(stack.pop())

        return parsed2

    def exec(self, parsed_exp):
        stack = []
        for token in parsed_exp:
            if token[1] == "NB":
                stack.append(self.convertFloatToIntIfPossible(float(token[0])))
            elif token[1] == "STR":
                stack.append(str(token[0]))
            elif token[1] == "OP":
                if token[2] == "plus":
                    try: b = stack.pop()
                    except: b = 1
                    try: a = stack.pop()
                    except: a = 1
                    try:
                        stack.append(a + b)
                    except:
                        stack.append(str(a) + str(b))
                elif token[2] == "minus":
                    try: b = stack.pop()
                    except: b = 1
                    try: a = stack.pop()
                    except: a = 1
                    stack.append(a - b)
                elif token[2] == "divide":
                    try: b = stack.pop()
                    except: b = 1
                    try: a = stack.pop()
                    except: a = 1
                    stack.append(a / b)
                elif token[2] == "mul":
                    try: b = stack.pop()
                    except: b = 1
                    try: a = stack.pop()
                    except: a = 1
                    stack.append(a * b)
                elif token[2] == "power":
                    try: b = stack.pop()
                    except: b = 1
                    try: a = stack.pop()
                    except: a = 1
                    stack.append(a ** b)
                elif token[2] == "is_equal":
                    try: b = stack.pop()
                    except: b = 1
                    try: a = stack.pop()
                    except: a = 1
                    stack.append(int(a == b))
                elif token[2] == "is_not_equal":
                    try: b = stack.pop()
                    except: b = 1
                    try: a = stack.pop()
                    except: a = 1
                    stack.append(int(a != b))
                elif token[2] == "more_equal":
                    try: b = stack.pop()
                    except: b = 1
                    try: a = stack.pop()
                    except: a = 1
                    stack.append(int(a >= b))
                elif token[2] == "less_equal":
                    try: b = stack.pop()
                    except: b = 1
                    try: a = stack.pop()
                    except: a = 1
                    stack.append(int(a <= b))
                elif token[2] == "more":
                    try: b = stack.pop()
                    except: b = 1
                    try: a = stack.pop()
                    except: a = 1
                    stack.append(int(a > b))
                elif token[2] == "less":
                    try: b = stack.pop()
                    except: b = 1
                    try: a = stack.pop()
                    except: a = 1
                    stack.append(int(a < b))
                elif token[2] == "concat":
                    b = stack.pop()
                    a = stack.pop()
                    if type(a) in [int, float] and type(b) in [int, float]:
                        stack.append(int(str(int(a)) + str(int(b))))
                    elif type(a) == str and type(b) == str:
                        stack.append(str(a) + str(b))
                    elif type(a) in [int, float]:
                        try:
                            stack.append(self.convertFloatToIntIfPossible(float(str(a) + str(b))))
                        except:
                            stack.append(str(str(a) + str(b)))
                    else:
                        stack.append(str(str(a) + str(b)))
        return stack[0] if stack else None
    
    def run(self, code:str):
        code = SourceCode(code)
        code = self.removeComments(code)
        c = []
        for l in code:
            c.append(l[1])
        self.parse_code("\n".join(c))

import os

shaft = Shaft()

path = "main.shf"
code = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), path)).read()

shaft.run(code)