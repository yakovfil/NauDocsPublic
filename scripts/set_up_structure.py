# Copyright 2025 N-GINN LLC. All rights reserved.
# Use of this source code is governed by a BSD-3 Clause license that can be found in the LICENSE file.

import os
import sys
import glob
import shutil
from pathlib import Path
from collections import defaultdict
import argparse

classes_title = 'Classes'
structs_title = 'Structures'
typedef_title = 'Typedefs'
using_title = 'Usings'
enums_title = 'Enumerations'
union_title = 'Unions'
functions_title = 'Functions'
macros_title = 'Macros'
variables_title = 'Variables'

enumerators_title = 'Enumerators'

type_entity_map = { 'class'     : classes_title, 
                    'struct'    : structs_title,
                    'typedef'   : typedef_title,
                    'using'     : using_title,
                    'enum'      : enums_title, 
                    'union'     : union_title,
                    'macro'     : macros_title,
                    'function'  : functions_title,
                    'variable'  : variables_title,
                    'enumerator': enumerators_title, 
                    }
entity_rst_map = {  'class'     : 'classes.rst',
                    'struct'    : 'classes.rst',
                    'typedef'   : 'types.rst',
                    'using'     : 'types.rst',
                    'enum'      : 'enums.rst',
                    'union'     : 'unions.rst',
                    'macro'     : 'macros.rst',
                    'function'  : 'functions.rst',
                    'variable'  : 'variables.rst',
                    'enumerator': 'enums.rst',
                    }
entity_page_map = { 'class'         : classes_title,
                    'struct'        : classes_title,
                    'typedef'       : typedef_title,
                    'using'         : typedef_title,
                    'enum'          : enums_title,
                    'union'         : union_title,
                    'macro'         : macros_title,
                    'function'      : functions_title,
                    'variable'      : variables_title,            
                    'enumerator'    : enumerators_title,
                    }
entity_sphinx_map = {   'class'     : ':cpp:class:', 
                        'struct'    : ':cpp:struct:',
                        'typedef'   : ':cpp:type:',
                        'using'     : ':cpp:type:',
                        'enum'      : ':cpp:enum:',
                        'union'     : ':cpp:union:',
                        'macro'     : ':c:macro:',
                        'function'  : ':cpp:func:',
                        'variable'  : ':cpp:var:',
                        'enumerator': ':cpp:enumerator:'
                        }

entity_breathefunc_map = {  'class'     : '.. doxygenclass:: ', 
                            'struct'    : '.. doxygenstruct:: ',
                            'typedef'   : '.. doxygentypedef:: ',
                            'using'     : '.. doxygentypedef:: ',
                            'enum'      : '.. doxygenenum:: ',
                            'union'     : '.. doxygenunion:: ',
                            'macro'     : '.. doxygendefine:: ',
                            'function'  : '.. doxygenfunction:: ',
                            'variable'  : '.. doxygenvariable::',
                            'enumerator': '.. doxygenenumvalue:: ',
                        }


generated_content_folder = 'generated_content'
section_entity_map = defaultdict(dict)

def parse_csvs(extracted_path, generated_path):
    shutil.rmtree(generated_path, ignore_errors=True) #GENERATED_CONTENT FOLDER GETS CLEARED!
    Path(generated_path).mkdir()
    for root, dirs, files in os.walk(extracted_path):
        for file in files:
            if file.endswith('.csv') and not file.endswith('Copy.csv'):
                csv_full_name = f'{root}/{file}'
                cached_data = open(csv_full_name).read()
                cached_lines = cached_data.splitlines()[1:]
                header_full_name = cached_lines[0].replace(';', '')
                for line in cached_lines[1:]:
                    entity_data = line.split(';')
                    entity_type = entity_data[0]
                    if entity_type in type_entity_map:
                        # (entity_name, entity_signature) = preproc_signature(entity_data[1], entity_data[4])
                        entity_name = entity_data[1]
                        entity_signature = entity_data[4]
                        section_full_name = 'Uncategorized' if entity_data[2] == '' else entity_data[2]
                        entity_brief = entity_data[3]
                        entity_args = entity_data[5] if len(entity_data) > 5 else ''
                        if entity_type not in section_entity_map[section_full_name]:
                            section_entity_map[section_full_name][entity_type] = []
                        section_entity_map[section_full_name][entity_type].append((entity_name, entity_brief, entity_signature, entity_args, header_full_name))
def make_indices(generated_path):
    for topic_full_name in glob.iglob(f'{generated_path}/**'):
        topic_full_name = topic_full_name.replace('\\', '/')
        for root, dirs, files in os.walk(topic_full_name):
            section_full_path = root.replace('\\', '/')
            section_full_name = section_full_path.replace(f'{generated_path}/', '')
            make_section_index(section_full_path, dirs, list(section_entity_map[section_full_name]))   
    make_main_index(generated_path)

def fill_briefs(generated_path):
    signature_command_map = {}
    for topic_full_name in glob.iglob(f'{generated_path}/**'):
        topic_full_name = topic_full_name.replace('\\', '/')
        for root, dirs, files in os.walk(topic_full_name):
            section_full_path = root.replace('\\', '/')
            section_full_name = section_full_path.replace(f'{generated_path}/', '')
            rst_col_widths_map = defaultdict(list)
            for entity_type, entities in section_entity_map[section_full_name].items():
                for entity_data in entities:
                    rst_full_name = root + '/' + entity_rst_map[entity_type]
                    if rst_full_name not in rst_col_widths_map:
                        rst_col_widths_map[rst_full_name] = [0, 0]
                    entity_name = entity_data[0]
                    entity_brief = entity_data[1]
                    entity_signature = preproc_signature(entity_data[2], entity_type)
                    sphinxcommand = f'{entity_sphinx_map[entity_type]}`{construct_entity_printed_cpp_name(entity_type, entity_name, entity_data[3])} <{entity_signature}>`'
                    rst_col_widths_map[rst_full_name][0] = max(rst_col_widths_map[rst_full_name][0], len(sphinxcommand)) # left column
                    rst_col_widths_map[rst_full_name][1] = max(rst_col_widths_map[rst_full_name][1], len(entity_brief)) # right column
                    signature_command_map[entity_data[2]] = sphinxcommand
            for entity_type, entities in section_entity_map[section_full_name].items():
                rst_full_name = root + '/' + entity_rst_map[entity_type]
                rst_content = '' if not os.path.isfile(rst_full_name) else open(rst_full_name).read()
                with open(rst_full_name, 'a') as rst:
                    if (rst_content == ''):
                        rst.write(f'{entity_page_map[entity_type]}\n==============\n\n')
                        rst.write(f'*{section_full_name}*\n\n')
                        rst.write('Brief descriptions\n-----------------------\n')
                        rst.write(  '.. table::\n'
                                    '   :width: 100%\n'
                                    '   \n')
                        rst.write(f"   +{'-'*rst_col_widths_map[rst_full_name][0]}-{'-'*(rst_col_widths_map[rst_full_name][1])}+\n")
                    rst.write(f"   |{type_entity_map[entity_type]}{' ' * (rst_col_widths_map[rst_full_name][0] + rst_col_widths_map[rst_full_name][1] + 1 - len(type_entity_map[entity_type]))}|\n")
                    rst.write(f"   +{'-'*rst_col_widths_map[rst_full_name][0]}+{'-'*(rst_col_widths_map[rst_full_name][1] )}+\n")
                    for entity_data in entities:
                        entity_name = entity_data[0]
                        entity_brief = entity_data[1]
                        sphinxcommand = signature_command_map[entity_data[2]]
                        rst.write(f"   |{sphinxcommand}{' '*(rst_col_widths_map[rst_full_name][0] - len(sphinxcommand))}|{entity_brief}{' '*(rst_col_widths_map[rst_full_name][1] - len(entity_brief))}|\n")
                        rst.write(f"   +{'-'*rst_col_widths_map[rst_full_name][0]}+{'-'*rst_col_widths_map[rst_full_name][1]}+\n")

def construct_entity_printed_cpp_name(entity_type, entity_short_name, entity_args):
    entity_args = entity_args.replace('<', '\\<') # to repair :cpp:... directive
    entity_printed_name = entity_short_name
    entity_printed_name = entity_printed_name.replace('anon_enum::', '')
    if entity_type == 'function' and has_namesakes(entity_type, entity_short_name):
        entity_printed_name = f"{entity_short_name}({entity_args})"
    elif (entity_type == 'class' or entity_type == 'struct') and entity_args != '':
        entity_printed_name = f"{entity_short_name}\\<{entity_args}>"
    return entity_printed_name
    
def preproc_signature(entity_signature, entity_type):
    if "anon_enum::" in entity_signature:
        entity_signature = entity_signature.rpartition('::')[2]
    if entity_type == 'macro':
        entity_signature = entity_signature.rpartition('::')[2]
    return entity_signature

def has_namesakes(entity_type, entity_name):
    namesakes_including_self = 0
    for section_full_name, entities_data in section_entity_map.items():
        if entity_type in entities_data:
            for entity_data in entities_data[entity_type]:
                if entity_name == entity_data[0]:
                    namesakes_including_self += 1
    return namesakes_including_self > 1

def fill_details(generated_path):
    for topic_full_name in glob.iglob(f'{generated_path}/**'):
        topic_full_name = topic_full_name.replace('\\', '/')
        for root, dirs, files in os.walk(topic_full_name):
            section_full_path = root.replace('\\', '/')
            section_full_name = section_full_path.replace(f'{generated_path}/', '')
            rst_opened_map = {}
            for entity_type, entities in section_entity_map[section_full_name].items():
                rst_full_name = root + '/' + entity_rst_map[entity_type]
                with open(rst_full_name, 'a') as rst:
                    if rst_full_name not in rst_opened_map:
                        rst.write('\n\nDetailed information\n-----------------------\n\n')
                    rst_opened_map[rst_full_name] = 1
                    for entity_data in entities[:-1]:
                        entity_name = entity_data[0]
                        entity_args = entity_data[3]
                        header = entity_data[4]
                        rst.write(f"{str.replace(entity_name, 'nau::', '')}\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
                        rst.write(f"``{header}``\n\n")
                        rst.write(make_breathecommand(entity_type, entity_name, entity_args))
                        rst.write('----------------------------------------------------\n\n')
                    header = entities[-1][4]
                    rst.write(f"{str.replace(entities[-1][0], 'nau::', '')}\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
                    rst.write(f"``{header}``\n\n")
                    rst.write(make_breathecommand(entity_type, entities[-1][0], entities[-1][3]))
                    rst.write('\n')

def make_breathecommand(entity_type, entity_name, entity_args):
    if entity_type == 'function':
        return f"{entity_breathefunc_map[entity_type]} {entity_name}({entity_args})\n\n"
    elif (entity_type == 'struct' or entity_type == 'class') and entity_args != '':
        return f"{entity_breathefunc_map[entity_type]} {entity_name}< {entity_args} >\n\n"
    else:
        return f"{entity_breathefunc_map[entity_type]} {entity_name}\n\n"

def make_section_index(section_full_path, subsections, entity_types):
        index_full_path = f"{section_full_path}/index.rst"
        section_short_name = str.rpartition(section_full_path, '/')[2]
        with open(index_full_path, 'w') as index:
            index.write(f"{section_short_name}\n==================\n\n")
            index.write(
                        '.. toctree::\n'
                        '   :maxdepth: 0\n'
                        '   :glob:\n\n'
                        )
            for subsection_name in subsections:
                index.write(f"   {subsection_name}/index\n")
            set_of_rsts = set()
            for entity_type in entity_types:
                set_of_rsts.add(entity_rst_map[entity_type])
            for rst in set_of_rsts:
                index.write(f"   {rst.partition('.rst')[0]}\n")

def make_main_index(generated_path):
    with open(generated_path.replace('generated_content', '') + 'index.rst', 'w') as index:
       index.write( '\n'
                    '.. toctree::\n'
                    '   :maxdepth: 0\n'
                    '   :glob:\n'
                    '   :hidden:\n'
                    '   :caption: Contents\n\n'
                    )
       for topic_path in glob.iglob(f"{generated_path}/**"):
            topic_path = topic_path.replace('\\', '/')
            topic_path = 'generated_content' + topic_path.replace(generated_path, '')
            index.write(f"   {topic_path}/index\n")
       preface = open(generated_path.replace('generated_content', '') + 'index_preface.rst', 'r').read()
       index.write('\n' + preface)
           
           


extracted_info_folder_name = 'extracted_info'
generated_content_folder_name = 'generated_content'

def main():
    version = sys.argv[1]
    prefix = ''
    # prefix = '../'
    extracted_path = prefix + 'source/' + version + '/api-doc/' + extracted_info_folder_name
    generated_path = prefix + 'source/' + version + '/api-doc/' + generated_content_folder_name
    parse_csvs(extracted_path, generated_path)
    for section in section_entity_map:
        os.makedirs(generated_path + '/' + section, exist_ok=True)
    fill_briefs(generated_path) #create rsts for entities and fill entities briefs
    fill_details(generated_path)
    make_indices(generated_path) #assemble indices


if __name__ == '__main__':
    main()