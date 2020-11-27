from datetime import datetime


def create_rendering_functions():
    functions = {
        'format_date': format_date,
        'format_json_date': format_json_date,
        'fixed_size': fixed_size,
        'lfixed': lfixed,
        'rfixed': rfixed,
        'nfixed': nfixed,
        'null_safe': null_safe,
        'lower': lower,
        'upper': upper
    }
    return functions


def format_date(input_value, input_date_format, output_date_format):
    json_date = str(input_value)
    if json_date is None or json_date == '':
        return ""
    formatted_date = datetime.strptime(json_date, input_date_format).strftime(output_date_format)
    return formatted_date


def format_json_date(input_value, date_format):
    return format_date(input_value, '%Y-%m-%d', date_format)


def fixed_size(input_value, string_size, prefix="{:<", postfix="}"):
    json_string = str(input_value)
    return (prefix + str(string_size) + postfix).format(json_string[:string_size])


def lfixed(input_value, string_size):
    return fixed_size(input_value, string_size)


def rfixed(input_value, string_size):
    return fixed_size(input_value, string_size, "{:>")


def nfixed(input_value, string_size):
    return fixed_size(input_value, string_size, "{:0>")


def null_safe(json_number):
    if json_number is None:
        return ""
    return json_number


def lower(input_value):
    json_string = str(input_value)
    return json_string.lower()


def upper(input_value):
    json_string = str(input_value)
    return json_string.upper()

