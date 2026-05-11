from enum import StrEnum


class VarTypeEnum(StrEnum):
    _string = "string"
    _int = "int"
    _double = "double"
    _float = "float"
    _bool = "bool"
    _byte = "byte"

    _string_array = "string[]"
    _int_array = "int[]"
    _double_array = "double[]"
    _float_array = "float[]"
    _bool_array = "bool[]"
    _byte_array = "byte[]"
