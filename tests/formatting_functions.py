from target_mako.formatting_functions import format_json_date, fixed_size, null_safe, format_date, lower, upper


def test_format_date():
    # given
    json_date = "28/08/2020"
    input_date_format = '%d/%m/%Y'
    output_date_format = '%d%m%Y'
    # when
    result = format_date(json_date, input_date_format, output_date_format)
    # then
    assert result is not None
    assert "28082020" == result


def test_format_date2():
    # given
    json_date = "08-28-2020"
    input_date_format = '%m-%d-%Y'
    output_date_format = '%d%m%Y'
    # when
    result = format_date(json_date, input_date_format, output_date_format)
    # then
    assert result is not None
    assert "28082020" == result


def test_format_json_date():
    # given
    json_date = "2020-08-28"
    date_format = '%d%m%Y'
    # when
    result = format_json_date(json_date, date_format)
    # then
    assert result is not None
    assert "28082020" == result


def test_fixed_size_smaller():
    # given
    json_string = "some content"
    string_size = 30
    # when
    result = fixed_size(json_string, string_size)
    # then
    assert result is not None
    assert string_size == len(result)


def test_fixed_size_bigger():
    # given
    json_string = "some content"
    string_size = 5
    # when
    result = fixed_size(json_string, string_size)
    # then
    assert result is not None
    assert string_size == len(result)


def test_fixed_size_integer():
    # given
    json_integer = 123
    string_size = 30
    # when
    result = fixed_size(json_integer, string_size)
    # then
    assert result is not None
    assert string_size == len(result)


def test_fixed_size_number():
    # given
    json_number = 123.0
    string_size = 30
    # when
    result = fixed_size(json_number, string_size)
    # then
    assert result is not None
    assert string_size == len(result)


def test_null_safe_none():
    # given
    json_number = None
    # when
    result = null_safe(json_number)
    # then
    assert result is not None
    assert "" == result


def test_null_safe_integer():
    # given
    json_number = 25
    # when
    result = null_safe(json_number)
    # then
    assert result is not None
    assert 25 == result


def test_null_safe_number():
    # given
    json_number = 25.00
    # when
    result = null_safe(json_number)
    # then
    assert result is not None
    assert 25.00 == result


def test_lower():
    # given
    json_string = 'MyString'
    # when
    result = lower(json_string)
    # then
    assert result is not None
    assert 'mystring' == result


def test_lower_boolean():
    # given
    json_boolean = True
    # when
    result = lower(json_boolean)
    # then
    assert result is not None
    assert 'true' == result


def test_lower_integer():
    # given
    json_integer = 100
    # when
    result = lower(json_integer)
    # then
    assert result is not None
    assert '100' == result


def test_lower_number():
    # given
    json_number = 100.00
    # when
    result = lower(json_number)
    # then
    assert result is not None
    assert '100.0' == result


def test_upper():
    # given
    json_string = 'MyString'
    # when
    result = upper(json_string)
    # then
    assert result is not None
    assert 'MYSTRING' == result


def test_upper_boolean():
    # given
    json_boolean = True
    # when
    result = upper(json_boolean)
    # then
    assert result is not None
    assert 'TRUE' == result


def test_upper_integer():
    # given
    json_integer = 100
    # when
    result = upper(json_integer)
    # then
    assert result is not None
    assert '100' == result


def test_upper_number():
    # given
    json_number = 100.00
    # when
    result = upper(json_number)
    # then
    assert result is not None
    assert '100.0' == result

