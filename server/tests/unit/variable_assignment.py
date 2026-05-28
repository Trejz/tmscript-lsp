def test_valid_int_assignment_has_no_diagnostics(diagnostics_rules, make_document):
    document = make_document(
        """
        int score = 10
        """
    )

    diagnostics = diagnostics_rules.var_value_assignmenet(document)

    assert diagnostics == []


def test_undefined_variable_assignment_reports_error(diagnostics_rules, make_document):
    document = make_document(
        """
        number = 10
        """
    )

    diagnostics = diagnostics_rules.var_value_assignmenet(document)

    assert any(d.message == "Variable not defined" for d in diagnostics)


def test_wrong_assignment(diagnostics_rules, make_document):
    document = make_document(
        """
        int var1 = "test"
        int var2 = 1.1
        int var3 = String_ToUpper()

        byte byte1 = "test"
        byte byte2 = 1.1
        byte byte3 = String_ToUpper()
        byte byte4 = -10

        float float1 = "test"
        float float2 = String_ToUpper()

        double double1 = "test"
        double double2 = String_ToUpper()



        """
    )
    """
        string str1 = 10
        string str2 = "test
        string str3 = test"
        string str4 = "test" + "test2
        string str5 = "test" + test2"
        string str6 = test" + test2"
        string str7 = "test + "test2"
        string str8 = Length()
        string str9 =
    """

    diagnostics = diagnostics_rules.var_value_assignmenet(document)
    
    messages: list[str] = [
                "Value is not a int",
                "Value is not a int",
                "Invalid type. Function returns: string",
                "Value is not a byte",
                "Value is not a byte",
                "Invalid type. Function returns: string",
                "Byte values can't have negative values",
                "Value is not a float",
                "Invalid type. Function returns: string",
                "Value is not a double",
                "Invalid type. Function returns: string"
            ]

    for i, d in enumerate(diagnostics):
        assert d.message == messages[i]

