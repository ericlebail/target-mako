#!/usr/bin/env python3

import argparse
import http.client
import io
import json
import os
import string
import sys
import threading
import urllib

import pkg_resources
import singer
from jsonschema.validators import Draft4Validator
from mako import exceptions
from mako.lookup import TemplateLookup

from target_mako.dict_proxy import wrap_namespace
from target_mako.formatting_functions import create_rendering_functions

LOGGER = singer.get_logger()


def emit_state(state):
    if state is not None:
        line = json.dumps(state)
        LOGGER.debug('Emitting state {}'.format(line))
        sys.stdout.write("{}\n".format(line))
        sys.stdout.flush()


def get_abs_path(path):
    path_os = path.replace("/", os.path.sep)
    pathname = os.path.join(os.getcwd(), path_os)
    return pathname


def load_config_for_stream(config, key, stream_id):
    value = None
    if key in config:
        value = config[key]
    if "stream_configs" in config and stream_id in config["stream_configs"] \
            and key in config["stream_configs"][stream_id]:
        value = config["stream_configs"][stream_id][key]
    return value


class TemplateValues:
    def __init__(self, d):
        for k, v in d.items():
            if isinstance(v, dict):
                v = TemplateValues(v)
            if isinstance(v, list):
                new_list = []
                for x in v:
                    if isinstance(x, dict):
                        new_list.append(TemplateValues(x))
                    else:
                        new_list.append(x)
                v = new_list
            self.__dict__[k] = v


def persist_lines(config, lines):
    state = None
    schemas = {}
    key_properties = {}
    headers = {}
    validators = {}
    templates = {}
    outputs = {}
    indexes = {}
    numbers = {}
    last_records = {}
    last_schemas = {}

    # Loop over lines from stdin
    LOGGER.info("Processing records")
    rendering_functions = create_rendering_functions()
    for line in lines:
        try:
            o = json.loads(line)
        except json.decoder.JSONDecodeError:
            LOGGER.error("Unable to parse:\n{}".format(line))
            raise

        if 'type' not in o:
            raise Exception("Line is missing required key 'type': {}".format(line))
        t = o['type']
        if 'stream' not in o:
            raise Exception("Line is missing required key 'stream': {}".format(line))
        stream = o['stream']

        if t == 'RECORD':
            if stream not in indexes:
                indexes[stream] = 0
            if stream not in numbers:
                numbers[stream] = 1
            line_index = indexes[stream]
            line_number = numbers[stream]
            record_values, schema_values, line_index, line_number = process_record(config, line_index, line_number, o,
                                                                                   outputs, schemas, templates,
                                                                                   validators, rendering_functions)
            # update current data
            indexes[stream] = line_index
            numbers[stream] = line_number
            last_records[stream] = record_values
            last_schemas[stream] = schema_values
            state = None
        elif t == 'STATE':
            LOGGER.debug('Setting state to {}'.format(o['value']))
            state = o['value']
        elif t == 'SCHEMA':
            LOGGER.info("Rendering stream : " + stream)
            schemas[stream] = o['schema']
            validators[stream] = Draft4Validator(o['schema'])
            if 'key_properties' not in o:
                raise Exception("key_properties field is required")
            key_properties[stream] = o['key_properties']
            # get Mako templates
            templates[stream] = load_template_list_from_config(config, stream)
            # Open the output file
            outputs[stream] = open_output_file_list(config, templates[stream], stream)
        else:
            raise Exception("Unknown message type {} in message {}"
                            .format(o['type'], o))

    # finally render the footer and close the files
    render_footers_and_close_output_files(outputs, last_records, last_schemas, templates, rendering_functions)
    return state


def load_template_from_config(config, template_lookup, template_list):
    header_template_name = config['header_template_name']
    header_template = None
    if header_template_name:
        header_template = template_lookup.get_template(header_template_name)
    line_template_name = config['data_template_name']
    line_template = None
    if line_template_name:
        line_template = template_lookup.get_template(line_template_name)
    footer_template_name = config['footer_template_name']
    footer_template = None
    if footer_template_name:
        footer_template = template_lookup.get_template(footer_template_name)
    output_file_name = config['output_file_name']
    one_file_per_record = False
    if "one_file_per_record" in config:
        one_file_per_record = config['one_file_per_record']
    template_list.append({"header": header_template, "line": line_template, "footer": footer_template,
                          "output_filename": output_file_name, "one_file_per_record": one_file_per_record})
    return template_list


def load_template_list_from_config(config, stream):
    LOGGER.info("Loading templates for stream : " + stream)
    template_dir = load_config_for_stream(config, 'template_dir', stream)
    # preprocessor is there to remove extra line inside generated content (On windows machines).
    template_lookup = TemplateLookup(directories=[get_abs_path(template_dir)],
                                     module_directory=config['cache_template_dir'],
                                     preprocessor=[lambda x: x.replace("\r\n", "\n")])
    template_config_list = load_config_for_stream(config, 'template_list', stream)
    template_list = []
    for template_config in template_config_list:
        template_list = load_template_from_config(template_config, template_lookup, template_list)
    return template_list


def open_output_file_list(config, template_list, stream):
    LOGGER.info("Initializing output files for stream : " + stream)
    output_file_list = {}
    output_dir = load_config_for_stream(config, 'output_dir', stream)
    for templates in template_list:
        one_file_per_record = templates['one_file_per_record']
        if not one_file_per_record:
            output_file_encoding = "utf8"
            if "output_file_encoding" in templates:
                output_file_encoding = templates['output_file_encoding']
            output_file_EOL = "\r\n"
            if "output_file_EOL" in templates:
                output_file_EOL = templates['output_file_EOL']
            output_filename = templates['output_filename']
            output_file_path = get_abs_path(output_dir) + '/' + output_filename
            directory = os.path.dirname(output_file_path)
            os.makedirs(directory, exist_ok=True)
            output_file = open(output_file_path, "w+", encoding=output_file_encoding, newline=output_file_EOL)
            output_file_list[output_filename] = output_file
    return output_file_list


def process_record(config, line_index, line_number, o, outputs, schemas, templates,
                   validators, rendering_functions):
    stream = o['stream']
    if stream not in schemas:
        raise Exception(
            "A record for stream {} was encountered before a corresponding schema".format(stream))
    output_file_list = outputs[stream]
    template_list = templates[stream]
    # Get schema for this record's stream
    schema = schemas[stream]
    # Validate record
    validators[stream].validate(o['record'])
    record_dict = o['record']
    # enrich record with processing specific values
    record_dict['record_index'] = line_index
    record_dict['record_number'] = line_number
    record_values = wrap_namespace(record_dict)
    schema_values = wrap_namespace(schema)
    for templates in template_list:
        one_file_per_record = templates['one_file_per_record']
        output_file = get_or_open_file_for_template(config, one_file_per_record, output_file_list, record_dict,
                                                    templates, stream)
        render_templates_for_record(line_index, one_file_per_record, output_file, record_values, schema_values,
                                    templates, rendering_functions)
    line_index += 1
    line_number += 1
    return record_values, schema_values, line_index, line_number


def render_templates_for_record(line_index, one_file_per_record, output_file, record_values, schema_values, templates,
                                rendering_functions):
    # if first record of the stream then generate header
    if line_index == 0 or one_file_per_record:
        if templates['header'] is not None:
            try:
                output_file.write(
                    templates['header'].render(record=record_values, schema=schema_values,
                                               functions=rendering_functions) + "\n")
            except AttributeError as exc:
                LOGGER.error(str(exc))
            except Exception:
                LOGGER.error(exceptions.text_error_template().render())
    # generate the line template
    if templates['line'] is not None:
        try:
            output_file.write(templates['line'].render(record=record_values, schema=schema_values,
                                                       functions=rendering_functions) + "\n")
        except AttributeError as exc:
            LOGGER.error(str(exc))
        except Exception:
            LOGGER.error(exceptions.text_error_template().render())
    if one_file_per_record:
        # add footer
        render_footer_and_close(output_file, record_values, schema_values, templates, rendering_functions)


def render_footer_and_close(output_file, record_values, schema_values, templates, rendering_functions):
    if templates['footer'] is not None:
        try:
            output_file.write(
                templates['footer'].render(record=record_values, schema=schema_values,
                                           functions=rendering_functions) + "\n")
        except AttributeError as exc:
            LOGGER.error(str(exc))
        except Exception:
            LOGGER.error(exceptions.text_error_template().render())
    # close the file
    output_file.close()


def get_or_open_file_for_template(config, one_file_per_record, output_file_list, record_dict, templates, stream):
    output_filename = templates['output_filename']
    if not one_file_per_record:
        # use the single file
        output_file = output_file_list[output_filename]
    else:
        # open a new file
        output_file_path = generate_output_file_path(config, output_filename, record_dict, stream)
        output_file_encoding = "utf8"
        if "output_file_encoding" in templates:
            output_file_encoding = templates['output_file_encoding']
        output_file_EOL = "\r\n"
        if "output_file_EOL" in templates:
            output_file_EOL = templates['output_file_EOL']
        directory = os.path.dirname(output_file_path)
        os.makedirs(directory, exist_ok=True)
        output_file = open(output_file_path, "w+", encoding=output_file_encoding, newline=output_file_EOL)
    return output_file


def generate_output_file_path(config, output_filename, record_dict, stream):
    formatter = BlankFormatter()
    output_dir = load_config_for_stream(config, 'output_dir', stream)
    final_file_name = formatter.format(output_filename, **record_dict)
    output_file_path = get_abs_path(output_dir) + '/' + final_file_name
    return output_file_path


def render_footers_and_close_output_files(outputs, last_records, last_schemas, templates,
                                          rendering_functions):
    LOGGER.info("Rendering footer and closing file")
    for stream in outputs:
        template_list = templates[stream]
        output_file_list = outputs[stream]
        record_values = last_records[stream]
        schema_values = last_schemas[stream]
        for template in template_list:
            output_filename = template['output_filename']
            one_file_per_record = template['one_file_per_record']
            if not one_file_per_record:
                output_file = output_file_list[output_filename]
                render_footer_and_close(output_file, record_values, schema_values, template, rendering_functions)


def send_usage_stats():
    try:
        version = pkg_resources.get_distribution('target-mako').version
        conn = http.client.HTTPConnection('collector.singer.io', timeout=10)
        conn.connect()
        params = {
            'e': 'se',
            'aid': 'singer',
            'se_ca': 'target-mako',
            'se_ac': 'open',
            'se_la': version,
        }
        conn.request('GET', '/i?' + urllib.parse.urlencode(params))
        response = conn.getresponse()
        conn.close()
    except:
        LOGGER.debug('Collection request failed')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Config file')
    args = parser.parse_args()

    if args.config:
        with open(args.config) as input_args:
            config = json.load(input_args)
    else:
        config = {}

    if not config.get('disable_collection', False):
        LOGGER.info('Sending version information to singer.io. ' +
                    'To disable sending anonymous usage data, set ' +
                    'the config parameter "disable_collection" to true')
        threading.Thread(target=send_usage_stats).start()

    input_state = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    state = persist_lines(config, input_state)

    emit_state(state)
    LOGGER.debug("Exiting normally")


if __name__ == '__main__':
    main()


class BlankFormatter(string.Formatter):
    def __init__(self, default=''):
        self.default = default

    def get_value(self, key, args, kwds):
        if isinstance(key, str):
            return kwds.get(key, self.default)
        else:
            return string.Formatter.get_value(key, args, kwds)
