from enum import StrEnum


class VarTypeEnum(StrEnum):
    string_ = "string"
    int_ = "int"
    double_ = "double"
    float_ = "float"
    bool_ = "bool"
    byte_ = "byte"

    string_array_ = "string[]"
    int_array_ = "int[]"
    double_array_ = "double[]"
    float_array_ = "float[]"
    bool_array_ = "bool[]"
    byte_array_ = "byte[]"
