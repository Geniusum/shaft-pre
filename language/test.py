from src.shaft import *
import os

script_path = os.path.dirname(os.path.abspath(__file__))

shaft_instance = Shaft()

file = "tests\main.shf"

code = open(os.path.join(script_path, file)).read()

shaft_instance.run(code)