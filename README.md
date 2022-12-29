# target-mako

This is a [Singer](https://singer.io) target that reads JSON-formatted data
following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This target uses [Mako](https://www.makotemplates.org/) templating engine to generate output files containing the stream data.

This target

- loads the configured templates using [Mako templating language](https://docs.makotemplates.org/en/latest/syntax.html#expression-substitution)
- write the configured header (if any) into each output files (Header uses the first record values)
- receive the streamed records
- for each record, write one block rendered from the template (using the record data) in each output file
- write the configured footer (if any) into each output files (Footer uses the last record values)

![Build status](https://travis-ci.com/ericlebail/target-mako.svg?branch=master)
[![codecov](https://codecov.io/gh/ericlebail/target-mako/branch/master/graph/badge.svg?token=C37SIU1IUG)](https://codecov.io/gh/ericlebail/target-mako)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![Python 3.10.2](https://img.shields.io/badge/python-3.10.2-blue.svg)](https://www.python.org/downloads/release/python-3102/)

[Sources on Github](https://github.com/ericlebail/target-mako)

[![Package on PyPI](https://img.shields.io/pypi/v/target-mako.svg)](https://pypi.org/project/target-mako/)

## Accessing data in templates:

- The record data can be used in the template with (Null/None values will be safely displayed as empty string)

        ${record.attribute.sub-attribute}
      
      
- The schema data can be used in the template with (Null/None values will be safely displayed as empty string)

        ${schema.attribute.sub-attribute}
        
- Some Internal data are provided by the target module:

    - record index is counting records starting from 0
    
            ${record.record_index}
    
    - Record number is counting records starting from 1
    
            ${record.record_number}

## Formatting functions
    
Some formatting function exists to help create your templates

- Protect against Null (Python None) values

First parameter is the data to format (example: record.attribute.sub-attribute)

        ${functions['null_safe'](record.attribute.sub-attribute)}

- Specify a fixed size for strings

First parameter is the data to format (example: record.attribute.sub-attribute)

Second parameter is the required size (integer)

        ${functions['fixed_size'](record.attribute.sub-attribute, 27)}

- Specify a fixed size for strings (align left)

First parameter is the data to format (example: record.attribute.sub-attribute)

Second parameter is the required size (integer)

        ${functions['lfixed'](record.attribute.sub-attribute, 27)}
        
- Specify a fixed size for strings (align rigth)

First parameter is the data to format (example: record.attribute.sub-attribute)

Second parameter is the required size (integer)

        ${functions['rfixed'](record.attribute.sub-attribute, 27)}
        
- Specify a fixed size for numbers (by adding 0 before the passed value)

First parameter is the data to format (example: record.attribute.sub-attribute)

Second parameter is the required size (integer)

        ${functions['nfixed '](record.attribute.sub-attribute, 27)}

- JSON Date formatting

First parameter is the data to format (must be a JSON date YYYY-mm-dd)

Second parameter is the output format in [Python date-time format](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior)
    
        ${functions['format_json_date'](record.attribute.sub-attribute,'%d%m%Y')}

- Date formatting

First parameter is the data to format

Second parameter is the input format in [Python date-time format](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior)

Third parameter is the output format in [Python date-time format](https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior)
    
        ${functions['format_date'](record.attribute.sub-attribute, '%d/%m/%Y','%d%m%Y')}

- Lower letters

First parameter is the data to format

        ${functions['lower'](record.attribute.sub-attribute)}

- Upper letters

First parameter is the data to format

        ${functions['upper'](record.attribute.sub-attribute)}

## Config file description:
       
Here is a sample config file:
   
       {
         "disable_collection": true,
         "cache_template_dir": "/temp/mako_modules",
         "template_dir": "../default-templates",
         "output_dir": "../default-output",
         "template_list": [
         ],
         "stream_configs": {
           "sample": {
             "template_dir": "../templates",
             "output_dir": "../output",
             "template_list": [
               {
                 "header_template_name": "csv/sample_header.template.csv",
                 "data_template_name": "csv/sample.template.csv",
                 "footer_template_name": "",
                 "output_file_name": "sample.csv",
                 "output_file_encoding": "utf8",
                 "output_file_EOL": "\r\n"
               },
               {
                 "header_template_name": "json/sample_header.template.json",
                 "data_template_name": "json/sample.template.json",
                 "footer_template_name": "json/sample_footer.template.json",
                 "output_file_name": "sample{record_index}.json",
                 "output_file_encoding": "utf8",
                 "output_file_EOL": "\r\n",
                 "one_file_per_record": true
               },
           }
         }
       }
   
### First part is "global configuration":

- "disable_collection" optional, to disable sending usage statistic to Singer platform.    
- "cache_template_dir" path to directory that will be used to cache templates content for Mako engine.

### Second part is default configuration for all streams:

- "template_dir" : path to the directory that contains the template files.
- "output_dir" : path to the directory that where the output files will be created.
- "template_list" : list of template for file generation. Each element of the list contains:
    - "header_template_name" : file name of the template file for header (can be empty).It is used once per stream at 
    the beginning.
    - "data_template_name" : file name of the template file for record. It is used once per record in the stream.
    - "footer_template_name" : file name of the template file for footer (can be empty). It is used once at the end of 
    the stream.
    - "output_file_name" : the name of the generated file (can contain variables in case of multiple file generation)
    - "output_file_encoding" : Optionnal the generated file encoding. Default value is "utf8". For possible value please refer to https://docs.python.org/3/library/io.html?highlight=newline#io.TextIOWrapper
    - "output_file_EOL" : Optionnal the generated file End Of Line. Default Value is "\r\n". For possible values please refer to https://docs.python.org/3/library/io.html?highlight=newline#io.TextIOWrapper
    - "one_file_per_record" : boolean, if true, the target will generate one file per record in the stream, 
    else it will generate one file containing all records (repeating the "data_template_name").

### Third part is stream specific configuration:

expected structure is:

       "stream_configs": {
           <stream-id1> : {},
           <stream-id2> : {}
       }

All values from second part (Default values) can be overridden for each stream.

---

Copyright &copy; 2020 elebail
