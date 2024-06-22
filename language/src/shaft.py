"""

Shaft Programming Language
By Genius_um
Created from the MazeGroup Research Institute
Under the name of MazeGroup
Started the 3 March 2024
MazeGroup, a French development organization

Interpreter version : 0.01 beta

---

Versions Notes :

---

Todo List :

"""

...;...; "Importation" ;...;...
"Description" "In this section will be imported all libraries."

from src.libs.imports import *

...;...; "Data declaration" ;...;...
"Description" "In this section will be declared all static data."

lexical = {
    "decimals": {
        "after": ["."]
    },
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
        "power": ["^"]
    },
    "delimitors": {
        "bracket_open": ["("],
        "bracket_close": [")"],
        "square_open": ["["],
        "square_close": ["]"],
        "curly_open": ["{"],
        "curly_close": ["}"],
        "semicolon": [";"]
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
    },
    "keywords": {
        "var_def": ["var", "variable"],
        "func_def": ["func", "function"]
    }
}

numbers = [*"0123456789"]
latin = [*"abcdefghijklmnopqrstuvwxyz"]
latin_upper = [*"ABCDEFGHIJKLMNOPQRSTUVWXYZ"]

...;...; "Main class" ;...;...

class Shaft():
    def __init__(self) -> None:
        self.strings = {}

        self.scopes = {
            "global": {
                "0x0": {
                    "name": "_GLOBAL_STACK",
                    "name_type": "variable",
                    "type": "list",
                    "value": []
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
        
        for line_number, line in code.getPaireLinesList():
            line = line.strip()
            current_line = ""
            if len(line) >= 2:
                if line[:2] in lexical["comments"]["one_line"]:
                    pass
                else:
                    for i, char in enumerate([*line]):
                        try: double = char + line[i + 1]
                        except: double = ""
                        if double in lexical["comments"]["multi_lines_open"]:
                            multi_lines = True
                        elif double in lexical["comments"]["multi_lines_close"]:
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
            r += rd.choice(numbers)
        if r in self.strings.keys():
            r = self.genStringID()
        return r
    
    def mkStringReference(self, string:str, id:str):
        self.strings[id] = string

    def refAllStrings(self, exp:str):
        ls = lexical["strings"]
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
        for k, ops in lexical["syn_operators"].items():
            for op in ops:
                exp = re.sub(r'(?<!\S)' + re.escape(op) + r'(?!\S)', ' ' + op + ' ', exp)

        exp = re.sub(r'(?<=\d|\))(?=[^\d\)])|(?<=[^\d\()])(?=\d|\()|(?<=\()(?=\d)|(?<=\d)(?=\))', ' ', exp)
        
        return " ".join(exp.split())
    
    def parse_code(self, code:SourceCode):
        self.segments = []
        self.flux = {
            "tokens": [],
            "mode": None,
            "start": True,
            "instruction": "",
            "index": 0
        }
        def segmentFlux():
            if not self.flux["start"]:
                self.segments.append({
                    "mode": self.flux["mode"],
                    "instruction": self.flux["instruction"],
                    "tokens": self.flux["tokens"]
                })
        for line_index, line_content in code.getPairLines().items():
            line_nb = line_index + 1
            for index, char in enumerate(line_content):
                self.flux["index"] = index

                if self.flux["start"]:
                    self.flux["instruction"] = ""
                    self.flux["start"] = False
                    self.flux["tokens"] = []
                    self.flux["mode"] = None
                
                if char == lexical["delimitors"]["semicolon"]:
                    segmentFlux()
                    self.flux["start"] = True
                else:
                    if not self.flux["mode"]:
                        self.flux["mode"] = "EXP"

                self.flux["instruction"] += char
        segmentFlux()
        print(self.segments)

    def convertFloatToIntIfPossible(self, num):
        if isinstance(num, float):
            if num.is_integer():
                return int(num)
        return float(num)

    def parseExp(self, exp:str):
        exp = exp.strip()
        # exp = self.refAllStrings(exp)
        tokens_ = self.split_spec(exp).split()
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
            if token[0] in numbers:
                type = "NB"
                nb_type = "INT"
                if "." in token:
                    nb_type = "DEC"
            if not type == "NB":
                if token[0] == "#":
                    token = self.getStringFromRefID(token)
                    type = "STR"
            for k, op in lexical["syn_operators"].items():
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
        scode = SourceCode(code)
        code = self.refAllStrings(scode.code)
        code = self.removeComments(SourceCode(code))
        c = []
        for l in code:
            c.append(l[1])
        self.parse_code(SourceCode("\n".join(c)))