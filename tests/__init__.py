import tempfile
from io import TextIOWrapper
from tempfile import TemporaryFile

from mako.lookup import TemplateLookup

from target_mako import get_abs_path, load_template_from_config, load_template_list_from_config, open_output_file_list, \
    render_templates_for_record, TemplateValues, render_footer_and_close, get_or_open_file_for_template, \
    generate_output_file_path, load_config_for_stream


def test_load_config_for_stream():
    # given
    config = {
        "template_dir": "templates",
    }
    # when
    config_value = load_config_for_stream(config, 'template_dir', 'my-stream')
    # then
    assert config_value is not None
    assert "templates" == config_value


def test_load_config_for_stream_specific():
    # given
    config = {
        "template_dir": "templates",
        "stream_configs": {
            "my-stream": {
                "template_dir": "templates2"
            }
        }
    }
    # when
    config_value = load_config_for_stream(config, 'template_dir', 'my-stream')
    # then
    assert config_value is not None
    assert "templates2" == config_value


def test_load_template_from_config():
    # given
    config = {
        "template_dir": "templates",
        "cache_template_dir": "temp/mako_modules"
    }
    template_config = {
        "header_template_name": "csv/sample_header.template.csv",
        "data_template_name": "csv/sample.template.csv",
        "footer_template_name": "",
        "output_file_name": "sample.csv"
    }
    template_lookup = TemplateLookup([get_abs_path(config['template_dir'])], config['cache_template_dir'])
    template_list = []
    # when
    template_list = load_template_from_config(template_config, template_lookup, template_list)
    # then
    assert template_list is not None
    assert 1 == len(template_list)
    assert "header" in template_list[0]
    assert template_list[0]["header"] is not None
    assert "line" in template_list[0]
    assert template_list[0]["line"] is not None
    assert "footer" in template_list[0]
    assert template_list[0]["footer"] is None
    assert "output_filename" in template_list[0]
    assert template_list[0]["output_filename"] is not None
    assert "one_file_per_record" in template_list[0]
    assert template_list[0]["one_file_per_record"] is False


def test_load_template_list_from_config():
    # given
    config = {
        "template_dir": "templates",
        "cache_template_dir": "temp/mako_modules",
        "template_list": [
            {
                "header_template_name": "csv/sample_header.template.csv",
                "data_template_name": "csv/sample.template.csv",
                "footer_template_name": "",
                "output_file_name": "sample.csv"
            },
            {
                "header_template_name": "json/sample_header.template.json",
                "data_template_name": "json/sample.template.json",
                "footer_template_name": "json/sample_footer.template.json",
                "output_file_name": "sample{record_index}.json",
                "one_file_per_record": True
            }
        ]
    }
    # when
    template_list = load_template_list_from_config(config, "my-stream")
    # then
    assert template_list is not None
    assert 2 == len(template_list)
    assert "header" in template_list[0]
    assert template_list[0]["header"] is not None
    assert "line" in template_list[0]
    assert template_list[0]["line"] is not None
    assert "footer" in template_list[0]
    assert template_list[0]["footer"] is None
    assert "output_filename" in template_list[0]
    assert template_list[0]["output_filename"] is not None
    assert "one_file_per_record" in template_list[0]
    assert template_list[0]["one_file_per_record"] is False
    assert "one_file_per_record" in template_list[1]
    assert template_list[1]["one_file_per_record"] is True


def test_load_template_list_from_config_stream_specific():
    # given
    config = {
        "template_dir": "default-templates",
        "cache_template_dir": "temp/mako_modules",
        "template_list": [
        ],
        "stream_configs": {
            "my-stream": {
                "template_dir": "templates",
                "template_list": [
                    {
                        "header_template_name": "csv/sample_header.template.csv",
                        "data_template_name": "csv/sample.template.csv",
                        "footer_template_name": "",
                        "output_file_name": "sample.csv"
                    },
                    {
                        "header_template_name": "json/sample_header.template.json",
                        "data_template_name": "json/sample.template.json",
                        "footer_template_name": "json/sample_footer.template.json",
                        "output_file_name": "sample{record_index}.json",
                        "one_file_per_record": True
                    }
                ]
            }
        }
    }
    # when
    template_list = load_template_list_from_config(config, "my-stream")
    # then
    assert template_list is not None
    assert 2 == len(template_list)
    assert "header" in template_list[0]
    assert template_list[0]["header"] is not None
    assert "line" in template_list[0]
    assert template_list[0]["line"] is not None
    assert "footer" in template_list[0]
    assert template_list[0]["footer"] is None
    assert "output_filename" in template_list[0]
    assert template_list[0]["output_filename"] is not None
    assert "one_file_per_record" in template_list[0]
    assert template_list[0]["one_file_per_record"] is False
    assert "one_file_per_record" in template_list[1]
    assert template_list[1]["one_file_per_record"] is True


def test_open_output_file_list():
    # given
    config = {
        "template_dir": "templates",
        "cache_template_dir": "temp/mako_modules",
        "output_dir": "output",
        "template_list": [
            {
                "header_template_name": "csv/sample_header.template.csv",
                "data_template_name": "csv/sample.template.csv",
                "footer_template_name": "",
                "output_file_name": "sample.csv"
            },
            {
                "header_template_name": "json/sample_header.template.json",
                "data_template_name": "json/sample.template.json",
                "footer_template_name": "json/sample_footer.template.json",
                "output_file_name": "sample{record_index}.json",
                "one_file_per_record": True
            }
        ]
    }
    template_list = load_template_list_from_config(config, "my-stream")
    # when
    output_file_list = open_output_file_list(config, template_list, "my-stream")
    # then
    assert output_file_list is not None
    assert 1 == len(output_file_list)
    assert "sample.csv" in output_file_list
    assert output_file_list["sample.csv"] is not None
    assert isinstance(output_file_list["sample.csv"], TextIOWrapper)
    output_file_list["sample.csv"].close()


def test_open_output_file_list_stream_specific():
    # given
    config = {
        "template_dir": "default-templates",
        "cache_template_dir": "temp/mako_modules",
        "output_dir": "default-output",
        "template_list": [
        ],
        "stream_configs": {
            "my-stream": {
                "template_dir": "templates",
                "output_dir": "output",
                "template_list": [
                    {
                        "header_template_name": "csv/sample_header.template.csv",
                        "data_template_name": "csv/sample.template.csv",
                        "footer_template_name": "",
                        "output_file_name": "sample.csv"
                    },
                    {
                        "header_template_name": "json/sample_header.template.json",
                        "data_template_name": "json/sample.template.json",
                        "footer_template_name": "json/sample_footer.template.json",
                        "output_file_name": "sample{record_index}.json",
                        "one_file_per_record": True
                    }
                ]
            }
        }
    }
    template_list = load_template_list_from_config(config, "my-stream")
    # when
    output_file_list = open_output_file_list(config, template_list, "my-stream")
    # then
    assert output_file_list is not None
    assert 1 == len(output_file_list)
    assert "sample.csv" in output_file_list
    assert output_file_list["sample.csv"] is not None
    assert isinstance(output_file_list["sample.csv"], TextIOWrapper)
    output_file_list["sample.csv"].close()


def prepare_data_for_rendering(config, stream):
    template_list = load_template_list_from_config(config, stream)
    templates = template_list[0]
    output_file = TemporaryFile("w+", encoding="utf8", newline='')
    record_dict = {
        "checked": False,
        "dimensions": {"width": 10, "height": 20},
        "id": 4529370162,
        "name": "Ward",
        "color": "red",
        "price": -6013876.97,
        "tags": ["giuWZuYElGsAQRrAVkwoPhEkmGYAEW", "KxRwOKWSnFSkKCvlCi", "OvenWokplmxxJgokYsaTZFccqBCXFs"],
        "hour": "11:05:30 PM"
    }
    record_values = TemplateValues(record_dict)
    schema = {}
    schema_values = TemplateValues(schema)
    rendering_functions = {}
    return output_file, record_values, schema_values, templates, rendering_functions


def test_render_templates_for_record():
    # given
    line_index = 0
    one_file_per_record = False
    config = {
        "template_dir": "templates",
        "cache_template_dir": "temp/mako_modules",
        "output_dir": "output",
        "template_list": [
            {
                "header_template_name": "csv/sample_header.template.csv",
                "data_template_name": "csv/sample.template.csv",
                "footer_template_name": "",
                "output_file_name": "sample.csv"
            }
        ]
    }
    output_file, record_values, schema_values, templates, rendering_functions = prepare_data_for_rendering(config,
                                                                                                           "my-stream")
    # when
    render_templates_for_record(line_index, one_file_per_record, output_file, record_values, schema_values,
                                templates, rendering_functions)
    # then
    output_file.seek(0)
    file_values = output_file.readlines()
    output_file.close()
    assert file_values is not None
    assert 2 == len(file_values)
    assert "ID;NAME;CHECKED;HOUR;HEIGHT;WIDTH;COLOR;PRICE;TAGS\n" == file_values[0]
    print(file_values[1])
    assert "4529370162;Ward;0;11:05:30 PM;20;10;red;-6013876.97 EUR; giuWZuYElGsAQRrAVkwoPhEkmGYAEW | " \
           "KxRwOKWSnFSkKCvlCi | OvenWokplmxxJgokYsaTZFccqBCXFs |;${i}\n" == file_values[1]


def test_render_templates_for_record_no_header():
    # given
    line_index = 0
    one_file_per_record = False
    config = {
        "template_dir": "templates",
        "cache_template_dir": "temp/mako_modules",
        "output_dir": "output",
        "template_list": [
            {
                "header_template_name": "",
                "data_template_name": "csv/sample.template.csv",
                "footer_template_name": "",
                "output_file_name": "sample.csv"
            }
        ]
    }
    output_file, record_values, schema_values, templates, rendering_functions = prepare_data_for_rendering(config,
                                                                                                           "my-stream")
    # when
    render_templates_for_record(line_index, one_file_per_record, output_file, record_values, schema_values,
                                templates, rendering_functions)
    # then
    output_file.seek(0)
    file_values = output_file.readlines()
    output_file.close()
    assert file_values is not None
    assert 1 == len(file_values)
    assert "4529370162;Ward;0;11:05:30 PM;20;10;red;-6013876.97 EUR; giuWZuYElGsAQRrAVkwoPhEkmGYAEW | " \
           "KxRwOKWSnFSkKCvlCi | OvenWokplmxxJgokYsaTZFccqBCXFs |;${i}\n" == file_values[0]


def test_render_templates_for_record_no_line():
    # given
    line_index = 0
    one_file_per_record = False
    config = {
        "template_dir": "templates",
        "cache_template_dir": "temp/mako_modules",
        "output_dir": "output",
        "template_list": [
            {
                "header_template_name": "csv/sample_header.template.csv",
                "data_template_name": "",
                "footer_template_name": "",
                "output_file_name": "sample.csv"
            }
        ]
    }
    output_file, record_values, schema_values, templates, rendering_functions = prepare_data_for_rendering(config,
                                                                                                           "my-stream")
    # when
    render_templates_for_record(line_index, one_file_per_record, output_file, record_values, schema_values,
                                templates, rendering_functions)
    # then
    output_file.seek(0)
    file_values = output_file.readlines()
    output_file.close()
    assert file_values is not None
    assert 1 == len(file_values)
    assert "ID;NAME;CHECKED;HOUR;HEIGHT;WIDTH;COLOR;PRICE;TAGS\n" == file_values[0]


def test_render_templates_for_record_one_file():
    # given
    line_index = 0
    one_file_per_record = True
    config = {
        "template_dir": "templates",
        "cache_template_dir": "temp/mako_modules",
        "output_dir": "output",
        "template_list": [
            {
                "header_template_name": "csv/sample_header.template.csv",
                "data_template_name": "csv/sample.template.csv",
                "footer_template_name": "csv/sample_header.template.csv",
                "output_file_name": "sample.csv"
            }
        ]
    }
    output_file, record_values, schema_values, templates, rendering_functions = prepare_data_for_rendering(config,
                                                                                                           "my-stream")
    # when
    render_templates_for_record(line_index, one_file_per_record, output_file, record_values, schema_values,
                                templates, rendering_functions)
    # then
    assert output_file.closed


def test_render_templates_for_record_missing_key():
    # given
    line_index = 0
    one_file_per_record = False
    config = {
        "template_dir": "templates",
        "cache_template_dir": "temp/mako_modules",
        "output_dir": "output",
        "template_list": [
            {
                "header_template_name": "",
                "data_template_name": "csv/sample_missing_key.template.csv",
                "footer_template_name": "",
                "output_file_name": "sample.csv"
            }
        ]
    }
    output_file, record_values, schema_values, templates, rendering_functions = prepare_data_for_rendering(config,
                                                                                                           "my-stream")
    # when
    render_templates_for_record(line_index, one_file_per_record, output_file, record_values, schema_values,
                                templates, rendering_functions)
    # then
    output_file.seek(0)
    file_values = output_file.readlines()
    output_file.close()
    assert file_values is not None
    assert 0 == len(file_values)


def test_render_footer_and_close():
    # given
    config = {
        "template_dir": "templates",
        "cache_template_dir": "temp/mako_modules",
        "output_dir": "output",
        "template_list": [
            {
                "header_template_name": "csv/sample_header.template.csv",
                "data_template_name": "csv/sample.template.csv",
                "footer_template_name": "csv/sample_header.template.csv",
                "output_file_name": "sample.csv"
            }
        ]
    }
    output_file, record_values, schema_values, templates, rendering_functions = prepare_data_for_rendering(config,
                                                                                                           "my-stream")
    # when
    render_footer_and_close(output_file, record_values, schema_values, templates, rendering_functions)
    # then
    assert output_file.closed


def test_get_or_open_file_for_template():
    # given
    config = {
        "template_dir": "templates",
        "cache_template_dir": "temp/mako_modules",
        "output_dir": "output",
        "template_list": [
            {
                "header_template_name": "csv/sample_header.template.csv",
                "data_template_name": "csv/sample.template.csv",
                "footer_template_name": "csv/sample_header.template.csv",
                "output_file_name": "sample.csv"
            }
        ]
    }
    one_file_per_record = False
    output_file_list = {}
    output_file = TemporaryFile("w+", encoding="utf8", newline='')
    output_file_list["sample.csv"] = output_file
    record_dict = {
        "checked": False,
        "dimensions": {"width": 10, "height": 20},
        "id": 4529370162,
        "name": "Ward",
        "color": "red",
        "price": -6013876.97,
        "tags": ["giuWZuYElGsAQRrAVkwoPhEkmGYAEW", "KxRwOKWSnFSkKCvlCi", "OvenWokplmxxJgokYsaTZFccqBCXFs"],
        "hour": "11:05:30 PM"
    }
    template_list = load_template_list_from_config(config, "my-stream")
    templates = template_list[0]
    # when
    tested_file = get_or_open_file_for_template(config, one_file_per_record, output_file_list, record_dict,
                                                templates, "my-stream")
    # then
    assert tested_file is not None
    assert tested_file.readable()
    assert tested_file.writable()
    tested_file.close()


def test_get_or_open_file_for_template_one_file():
    # given
    config = {
        "template_dir": "templates",
        "cache_template_dir": "temp/mako_modules",
        "output_dir": "output",
        "template_list": [
            {
                "header_template_name": "csv/sample_header.template.csv",
                "data_template_name": "csv/sample.template.csv",
                "footer_template_name": "csv/sample_header.template.csv",
                "output_file_name": "sample.csv"
            }
        ]
    }
    one_file_per_record = True
    output_file_list = {}
    output_file = TemporaryFile("w+", encoding="utf8", newline='')
    output_file_list["sample.csv"] = output_file
    record_dict = {
        "checked": False,
        "dimensions": {"width": 10, "height": 20},
        "id": 4529370162,
        "name": "Ward",
        "color": "red",
        "price": -6013876.97,
        "tags": ["giuWZuYElGsAQRrAVkwoPhEkmGYAEW", "KxRwOKWSnFSkKCvlCi", "OvenWokplmxxJgokYsaTZFccqBCXFs"],
        "hour": "11:05:30 PM"
    }
    template_list = load_template_list_from_config(config, "my-stream")
    templates = template_list[0]
    # when
    tested_file = get_or_open_file_for_template(config, one_file_per_record, output_file_list, record_dict,
                                                templates, "my-stream")
    # then
    assert tested_file is not None
    assert tested_file.readable()
    assert tested_file.writable()
    tested_file.close()


def test_generate_output_file_path_integer():
    # given
    config = {
        "output_dir": "output"
    }
    output_filename = "sample{record_index}.json"
    record_dict = {
        "record_index": 123
    }
    # when
    result = generate_output_file_path(config, output_filename, record_dict, "my-stream")
    # then
    assert result is not None
    assert result.endswith("output/sample123.json")


def test_generate_output_file_path_string():
    # given
    config = {
        "output_dir": "output"
    }
    output_filename = "sample{record_index}.json"
    record_dict = {
        "record_index": "blabla"
    }
    # when
    result = generate_output_file_path(config, output_filename, record_dict, "my-stream")
    # then
    assert result is not None
    assert result.endswith("output/sampleblabla.json")


def test_generate_output_file_path_no_value():
    # given
    config = {
        "output_dir": "output"
    }
    output_filename = "sample{record_index}.json"
    record_dict = {
        "record_index2": 123
    }
    # when
    result = generate_output_file_path(config, output_filename, record_dict, "my-stream")
    # then
    assert result is not None
    assert result.endswith("output/sample.json")


def test_generate_output_file_path_no_key():
    # given
    config = {
        "output_dir": "output"
    }
    output_filename = "sample.json"
    record_dict = {
        "record_index": 123
    }
    # when
    result = generate_output_file_path(config, output_filename, record_dict, "my-stream")
    # then
    assert result is not None
    assert result.endswith("output/sample.json")
