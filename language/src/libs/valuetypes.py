class ShaftValueTypes():
    def __new__(cls) -> dict:
        return {
            "integer": ["int", "integer"],
            "string": ["string", "str"],
            "array": ["list", "array"],
            "decimal": ["decimal", "float"],
            "boolean": ["boolean", "bool"]
        }