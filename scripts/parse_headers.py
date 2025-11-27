# Copyright 2025 N-GINN LLC. All rights reserved.
# Use of this source code is governed by a BSD-3 Clause license that can be found in the LICENSE file.

from anytree import Node, RenderTree, PreOrderIter
import re
import sys
from itertools import repeat
from pathlib import Path
from collections import defaultdict
import argparse
import os


root = Node('root', type='file', entity_name='', stopped_at=0, scope_start=0, scope_end=sys.maxsize, signature='', brief='', args='')
fun_signature_dec_impl = {} #for each function signature tracks whether a declaration or an implementation has been parsed

entities_patterns = {
    'class'         : r'^[ \t]*(template[ \t]*<[^;{]*>\s*)?(?P<cl1_omit>class)[ \t]+(\w+[ \t])*(?P<class>[\w()]+)[ \t]*(<(?P<c_targs>[^{;:]*)>)?(?P<cl2_omit>(\s*:[^{;]*)?)\s*{', # reject forward declarations
    'struct'        : r'^[ \t]*(template[ \t]*<[^;{]*>\s*)?(?P<st_omit>struct)[ \t]+(\w+[ \t])*(?P<struct>(([\w]*::)*[\w()]+))[ \t]*(<(?P<s_targs>(([\w<>]*::)*[\w()<>]+)*)>)?(?P<st2_omit>(\s*:[^{;]*)?)\s*{',
    'typedef'       : r'^[ \t]*(?P<ty_omit>typedef +\w+ +)(?P<typedef>\w+);',
    'using'         : r'^[ \t]*(?P<us1_omit>using +)(?P<using>[\w<>()]+)(?P<us2_omit> *=\s*[^;]+);',
    'namespace'     : r'^[ \t]*(?P<na_omit>namespace +)(?P<namespace>[\w:]+)[^{]*{',
    'enum'          : r'^[ \t]*(?P<en1_omit>enum( +class)?) +(?P<enum>(?!class )\w+)(?P<en2_omit>(\s*:[^{;]+)?\s*){',
    'anon_enum'     : r'^[ \t]*(?P<ae_omit>(?P<anon_enum>enum( +class)?))([^;{]+)?{',
    'union'         : r'^[ \t]*(?P<un_omit>(typedef +)?union +)(?P<union>\w+)\s*{',
    'anon_union'    : r'^[ \t]*(?P<au_omit>(typedef +))(?P<anon_union>union?)([^{]+)?{',
    'macro'         : r'^[ \t]*(?P<ma1_omit>#define +)(?P<macro>\w+)(?P<ma2_omit>[^\n]+)?', #we ignore macro arguments as we can't handle macro overloads now
    'function'      : r'^[ \t]*(template[ \t]*<[^;{]*>\s*)?(requires\([^)]+\)\s*)?(([\w*&<>~_()]|(::))+ +[*&]*)*(?P<scope>[\w*&<>~_()]+::)*(?P<function>([\w~]+)|operator.)(?<!__declspec)\((?P<args>[^)]*)\)( *: [^{;]*)?[^;{=]*(?P<fu_omit> * = *\w+)?[;{]',
    'variable'      : r'(^[ \t]*(?P<va1_omit>(([\w<>*&]|(::))+[\s])+[*&]*)+(?P<variable>(?<!(struct ))(?<!(class ))(?<!(using ))(?<!(typedef ))(?<!(union ))(?<!(enum ))(?<!(#define ))(?<!(namespace ))\w+)(?P<va2_omit>\s*(=\s*[\w*&:<>\'\"~]+\s*)?);)',
    'enumerator'    : r'^[ \t]*(?P<enumerator>\w+)(?P<enu_omit>( *= *[^\s,]+)? *),*',
}

scope_registered_entities = {
    'file'      : ['class', 'struct', 'typedef', 'using', 'namespace', 'enum', 'anon_enum', 'union', 'anon_union', 'macro', 'function', 'variable'],
    'namespace' : ['class', 'struct', 'typedef', 'using', 'namespace', 'enum', 'anon_enum', 'union', 'anon_union', 'macro', 'function', 'variable'],
    'typedef'   : [],
    'using'     : [],
    'class'     : [],
    'struct'    : [],
    'function'  : [],
    'enum'      : [],
    'anon_enum' : ['enumerator'],
    'union'     : [],
    'anon_union' : ['variable'],
    'macro'     : [],
    'variable'  : [],
    'enumerator': []
}

entity_supports_scope = {
        'file'      : True,
        'namespace' : True,
        'class'     : True,
        'struct'    : True,
        'typedef'   : False,
        'using'     : False,
        'function'  : True,
        'enum'      : True,
        'anon_enum' : True,
        'union'     : True,
        'anon_union': True,
        'macro'     : False,
        'variable'  : False,
        'enumerator': False
}

def parse_conf(conf):
    conf_section_text = {
        'SOURCES': re.search(r'SOURCES\n{(?P<section_content>.*?)^}', conf, re.DOTALL|re.MULTILINE).group('section_content'),
        'GLOBAL_INCLUDE/EXCLUDES': re.search(r'GLOBAL_INCLUDE/EXCLUDES\n{(?P<section_content>.*?)^}', conf, re.DOTALL|re.MULTILINE).group('section_content'),
        'FILE_CONFIGS': re.search(r'FILE_CONFIGS\n{(?P<section_content>.*?)^}', conf, re.DOTALL|re.MULTILINE).group('section_content'),
        'MACRO_SYMBOLS': re.search(r'MACRO_SYMBOLS\n{(?P<section_content>.*?)^}', conf, re.DOTALL|re.MULTILINE).group('section_content'),
    }
    src_dirs={}
    global_excludes=[]
    global_excludes_post=[]
    excluded_files = []
    files_excludes = defaultdict(list)
    files_excludes_post = defaultdict()
    files_includes = defaultdict(list)
    src_dir_pattern = r'^\t(?P<topic>\w+) (?P<source_dir>[^\n]+)'
    file_config_pattern = r'^\t(?P<file>[\w.]+)\n(\t{\n(?P<config>[^}]*)\n\t})'
    file_to_exclude_pattern = r'^\t-(?P<file>[\w.]+)\n'
    exclude_pattern = r'^\s*-(?P<exclude>[^\n]+)'
    exclude_post_pattern = r'^\s*~(?P<exclude_post>[^\n]+)'
    include_pattern = r'^\s*\+(?P<include>[^\n]+)'
    for src_dirs_match in re.finditer(src_dir_pattern, conf_section_text['SOURCES'], re.MULTILINE):
        src_dirs[src_dirs_match.group('topic')] = src_dirs_match.group('source_dir')
    for global_exclude_match in re.finditer(exclude_pattern, conf_section_text['GLOBAL_INCLUDE/EXCLUDES'], re.MULTILINE):
        global_excludes.append(global_exclude_match.group('exclude'))
    for global_exclude_post_match in re.finditer(exclude_post_pattern, conf_section_text['GLOBAL_INCLUDE/EXCLUDES'], re.MULTILINE):
        global_excludes_post.append(global_exclude_post_match.group('exclude_post'))
    for excluded_file in re.finditer(file_to_exclude_pattern, conf_section_text['FILE_CONFIGS'], re.MULTILINE):
        excluded_files.append(excluded_file.group('file'))
    for file_match in re.finditer(file_config_pattern, conf_section_text['FILE_CONFIGS'], re.MULTILINE):
        if (not file_match.group('file') in excluded_files):
            config = file_match.group('config')
            files_excludes[file_match.group('file')] = []
            files_excludes_post[file_match.group('file')] = []
            files_includes[file_match.group('file')] = []
            for exclude_match in re.finditer(exclude_pattern, config, re.MULTILINE):
                files_excludes[file_match.group('file')].append(exclude_match.group('exclude'))
            for exclude_post_match in re.finditer(exclude_post_pattern, config, re.MULTILINE):
                files_excludes_post[file_match.group('file')].append(exclude_post_match.group('exclude_post'))
            for include_match in re.finditer(include_pattern, config, re.MULTILINE):
                files_includes[file_match.group('file')].append(include_match.group('include'))
    defined_symbols = {}
    for macro_line in conf_section_text['MACRO_SYMBOLS'].splitlines():
        macro_with_value_pattern = r'(?P<macro>\w+)=(?P<value>.+)$'
        macro_without_value_pattern = r'(?P<macro>\w+)$'
        if re.search(macro_with_value_pattern, macro_line):
            defined_symbols[re.search(macro_with_value_pattern, macro_line).group('macro')] = re.search(macro_with_value_pattern, macro_line).group('value')
        elif re.search(macro_without_value_pattern, macro_line):
            defined_symbols[re.search(macro_without_value_pattern, macro_line).group('macro')] = 'True'
    return (src_dirs, excluded_files, global_excludes, global_excludes_post, files_excludes, files_excludes_post, files_includes, defined_symbols)

def parse_cond_macro(code, defined_symbols):
    stopped_at = 0
    scope_starts = []
    scope_ends = []
    for line in code.splitlines():
        if '#if' in line:
            scope_starts.append(stopped_at)
            stopped_at += len(line) + 1
        elif '#endif' in line:
            scope_start = scope_starts.pop()
            scope_end = stopped_at + len(line) + 1
            processed_code = evaluate_cond_macro(code[scope_start : scope_end], defined_symbols)
            code = code[:scope_start] + processed_code + code[scope_end:]
            stopped_at = scope_start + len(processed_code)
        else:
            stopped_at += len(line) + 1
    return code

cond_macro_pattern = re.compile(r'^(?P<if>^[ \t]*#(if|ifdef|ifndef) [^\n]+\n(.(?!#elif|#else|#endif))*)\n((?P<elifs>^[ \t]*#elif [^\n]+\n((.(?!#else|#endif))*))\n)?((?P<else>^[ \t]*#else\s*\n(.(?!#else|#endif))*)\n)?[ \t]*#endif', re.MULTILINE | re.DOTALL)
if_pattern = re.compile(r'^[ \t]*#(if|ifdef|ifndef) (?P<if_condition>[^\n]*)\n(?P<if_effect>(.(?!#elif|#else|#endif))*)', re.MULTILINE | re.DOTALL)
elif_pattern = re.compile(r'^[ \t]*#elif (?P<elif_condition>[^\n]*)\n(?P<elif_effect>(.(?!#elif|#else|#endif))*)', re.MULTILINE | re.DOTALL)
else_pattern = re.compile(r'^[ \t]*#else\s*\n(?P<else_effect>(.(?!#endif))*)', re.MULTILINE | re.DOTALL)
#symbol_in_cond_pattern = re.compile(r'(?P<expr1>([!\w()]+)(?= *(==|!=|<=|>=|<|>)))|(?P<expr2>([!\w()]+)(?= *(\||&)))|((?<=(\||&)) *(?P<expr3>[\w!()]+))|(^ *(?P<expr4>[\w!()]+) *$)')
symbol_in_cond_pattern = re.compile(r'\b[\w]+\b')
do_not_substitute_in_cond_pattern = re.compile(r'\b[0-9]+\b')
defined_pattern = re.compile(r'defined *\( *(?P<symbol>.+?) *\)')

def evaluate_cond_macro(code, defined_symbols):
    cond_macro_match = cond_macro_pattern.search(code)
    if cond_macro_match:
        cond_macro_text = cond_macro_match.group()
        if_match = if_pattern.search(cond_macro_match.group('if'))
        if_conditions = [if_match.group('if_condition')]
        if if_match.group().startswith('#ifdef'):
            if_conditions = [f'defined({if_match.group('if_condition')})']
        elif if_match.group().startswith('#ifndef'):
            if_conditions = [f'!defined({if_match.group('if_condition')})']        
        if_effects = [if_match.group('if_effect')]
        if cond_macro_match.group('elifs'):
            for elif_match in elif_pattern.finditer(cond_macro_match.group('elifs')):
                if_conditions.append(elif_match.group('elif_condition'))
                if_effects.append(elif_match.group('elif_effect'))
        for i in range(len(if_conditions)):
            for defined_match in defined_pattern.finditer(if_conditions[i]):
                symbol = defined_match.group('symbol')
                if_conditions[i] = if_conditions[i].replace(defined_match.group(), f'{symbol in defined_symbols}')
            for symbol_match in symbol_in_cond_pattern.finditer(if_conditions[i]):
                symbol = symbol_match.group()
                if 'True' != symbol and 'False' != symbol and not do_not_substitute_in_cond_pattern.search(symbol):
                    if_conditions[i] = if_conditions[i].replace(symbol, defined_symbols[symbol] if symbol in defined_symbols else 'False')
            if_conditions[i] = if_conditions[i].replace('||', ' or ')
            if_conditions[i] = if_conditions[i].replace('|', ' or ')
            if_conditions[i] = if_conditions[i].replace('&&', ' and ')
            if_conditions[i] = if_conditions[i].replace('&', ' and ')
            if_conditions[i] = if_conditions[i].replace('!', ' not ')
            if eval(if_conditions[i]):
                return code.replace(cond_macro_match.group(), if_effects[i])
        if cond_macro_match.group('else'):
            else_match = else_pattern.search(cond_macro_match.group('else'))
            if else_match:
                return code.replace(cond_macro_match.group(), else_match.group('else_effect'))
    return ''

function_arg_pattern = r'(?P<argument>([\w<>*&:]+[\s]+[*&]*)+)(\s*\w+\s*)?,?'
template_arg_pattern = r'(?P<targument>[\w<>*&:]+)\s*,?\s*'

comment_block_pattern = r'^ *\/\*\*?(?P<comment_block>((?!\*\/).)*?)\*\/'
one_line_comment = r'\/\*\* *< *(?P<one_line_comment>.*?)\*\/'
standard_comment = r'//[^\n]*'

brief_pattern = r'@brief (?P<brief>[^\n]*)'

cond_pattern = r'\/\*\*\s*@ *cond\s*\*\/.*?\/\*\*\s*@ *endcond\s*\*\/' # skipped both by doxygen and the parser
skip_pattern = r'\/\*\*\s*@ *skip\s*\*\/.*?\/\*\*\s*@ *endskip\s*\*\/' # skipped only by the parser
remove_macro_bodies_pattern = r'^ *#define \w+(?P<body>([^\n]+\\\n)*[^\n]*)'
remove_scope_operator_pattern = r'(?<=[\s<{\()])::'
current_scope_code = ''

def parse_code(code, excludes, defined_symbols):
    clean_code = code
    for macro_match in re.compile(remove_macro_bodies_pattern, re.DOTALL|re.MULTILINE).finditer(clean_code):
        clean_code = clean_code.replace(macro_match.group(), macro_match.group().replace(macro_match.group('body'), ''))
    clean_code = re.compile(cond_pattern, re.DOTALL|re.MULTILINE).sub('', clean_code)
    clean_code = re.compile(skip_pattern, re.DOTALL|re.MULTILINE).sub('', clean_code)
    clean_code = re.compile(fr'({comment_block_pattern})|({one_line_comment})|({standard_comment})', re.DOTALL|re.MULTILINE).sub('', clean_code)
    # clean_code = re.compile(remove_scope_operator_pattern, re.DOTALL|re.MULTILINE).sub('', clean_code)
    clean_code = parse_cond_macro(clean_code, defined_symbols)
    for exclude in excludes:
        clean_code = re.compile(fr'{exclude}', re.MULTILINE|re.DOTALL).sub('', clean_code)
    current_node = root
    current_scope = 'file'
    while current_node:
        current_scope_code = clean_code[current_node.stopped_at:current_node.scope_end]
        (match, entity_type) = match_definition(clean_code, current_scope, current_node.stopped_at, current_node.scope_end)
        if not match:
            current_node = current_node.parent
            current_scope = current_node.type if current_node else ''
            continue
        entity_short_name = match.group(entity_type)
        new_scope_end = isolate_scope(clean_code, match.end() - 1, entity_type)
        current_node.stopped_at = new_scope_end
        if (must_keep(entity_type, match)):
            current_node = Node(name=entity_short_name, 
                            parent=current_node, 
                            entity_name=f'{current_node.entity_name}::{entity_short_name}', 
                            type=entity_type)
            current_node.scope_start = match.end() - 1
            current_node.stopped_at = match.end() - 1
            current_node.scope_end = new_scope_end
            current_node = modify_node_attributes(current_node, match)
            current_node.brief = parse_brief(code, match.group())
            current_scope = current_node.type
    # print(RenderTree(root))

# check whether the function declaration has already been parsed and if so (i.e. its implementation is being parsed) we will discard current entity
def must_keep(entity_type, match): #signature has to end with a ';; or with a '{'
    if entity_type != 'function':
        return True
    if (match.group('scope')):
        return False #means we are dealing with separated definition 
    signature = match.group()
    decl_or_impl = 'decl' if signature.endswith(';') else 'impl_or_decl'
    if signature[:-1] in fun_signature_dec_impl:
        if fun_signature_dec_impl[signature[:-1]] == 'impl_or_decl' and decl_or_impl == 'decl':
            fun_signature_dec_impl[signature[:-1]] = 'decl'
            return True
        else:
            return False
    else:
        fun_signature_dec_impl[signature[:-1]] = decl_or_impl
        return True

def isolate_scope(code, start, entity_type):
    balance = 0
    smcln_match = re.compile(r';').search(code, start)
    smcln_pos = smcln_match.start() if smcln_match else sys.maxsize - 1
    start_match = re.compile(r'{').search(code, start)
    start_pos = start_match.start() if start_match else sys.maxsize
    if not entity_supports_scope[entity_type] or smcln_pos < start_pos:
        return start+1
    scope_pattern = r'{|}'
    for match in re.compile(scope_pattern).finditer(code, start):
        if match.group() == '{':
            balance += 1
        elif match.group() == '}':
            balance -= 1
        if balance == 0:
            return match.end()

def match_definition(code, scope, start, end):
    current_code_block = code[start:end]
    pattern = r'(^\b$)'
    for e, p in entities_patterns.items():
        if e in scope_registered_entities[scope]:
            pattern = fr'{pattern}|({p})'
    match = re.compile(pattern, re.DOTALL|re.MULTILINE).search(code, start, end)
    if not match:
        return (None, '')
    for entity_type in entities_patterns:
        if entity_type in scope_registered_entities[scope] and match.group(entity_type):
            return (match, entity_type)
    assert(False)

def modify_node_attributes(node, match):
    node.args = ''
    signature = match.group()
    groups = match.groupdict()
    for group in groups:
        if group.endswith('omit') and match.group(group):
            signature = signature.replace(match.group(group), '')
        elif group.endswith('args') and match.group(group):
            node.args = match.group(group).replace('\n', ' ')
            # signature = signature.replace(match.group(group), re.sub(foul_pattern, '', match.group(group)))
    if signature.endswith(';') or signature.endswith('{') or signature.endswith(','):
        signature = signature[:-1] # remove ending { or ;
    signature = re.compile(r'(\n)', re.MULTILINE).sub(' ', signature) # remove \n's from signature
    node.signature = signature
    if node.parent.parent == None:
        node.entity_name = node.entity_name[2:] # erase '::' at the beginning
    if node.type == 'anon_enum':
        name_base = node.entity_name.rpartition('::')[0] + '::' if node.entity_name.rpartition('::')[0] != '' else ''
        node.entity_name = name_base + 'anon_enum'
        node.name = 'anon_enum'
    if node.type == 'anon_union':
        name_base = node.entity_name.rpartition('::')[0] + '::' if node.entity_name.rpartition('::')[0] != '' else ''
        node.entity_name = name_base + 'anon_union'
        node.name = 'anon_union'      
    
    return node

def parse_function_args(args):
    arg_list = []
    for match in re.finditer(function_arg_pattern, args):
        arg_list.append(match.group('argument'))
    return arg_list

def parse_template_args(targs):
    targ_list = []
    for match in re.finditer(template_arg_pattern, targs):
        targ_list.append(match.group('targument'))
    return targ_list

def parse_brief(code, signature):
    if signature.endswith(';') or signature.endswith('{'):
        signature = signature[:-1]
    if signature.endswith('\n'):
        signature = signature[:-1]
    signature = re.escape(signature)
    pattern = fr'({comment_block_pattern}\s*{signature})|({signature}\s*{one_line_comment})'
    match = re.compile(pattern, re.DOTALL|re.MULTILINE).search(code)
    if match:
        match_s = match.group()
        if match.group('comment_block'):
            return re.search(brief_pattern, match.group('comment_block'), re.MULTILINE).group('brief') if re.search(brief_pattern, match.group('comment_block'), re.MULTILINE) else ' '
        elif match.group('one_line_comment'):
            return match.group('one_line_comment') if match.group('one_line_comment') else ' '
    return ' '

def postproc(name, type, signature, args, excludes_post):
    for exclude in excludes_post:
        signature = re.compile(exclude).sub('', signature)
        args = re.compile(exclude).sub('', args)
    if type == 'macro':
        new_name = name.rpartition('::')[2]
        signature = signature.replace(name, new_name)
        name = new_name
    # if type == 'class' or type == 'struct':
    #     arg_array = []
    #     for arg in args.split(','):
    #         if arg.strip().startswith('::'):
    #             arg = arg[2:]
    #         arg_array.append(arg)
    #     args = ''
    #     for arg in arg_array:
    #         args += arg + ', '
    #     args = args[:2]
    return (name, signature, args)

def update_csv(path_to_csv, includes, excludes_post, topic, path_to_header):
    if not Path(path_to_csv).exists():
        with open(path_to_csv, 'w') as csv:
            csv.write('sep=;\n')
            csv.write(f'{path_to_header};\n')
            for node in PreOrderIter(root):
                name = node.entity_name
                entity_type = node.type
                signature = node.signature.replace(node.name, name)
                (name, signature, args) = postproc(name, entity_type, signature, node.args, excludes_post)
                csv.write(f'{node.type};{name};{topic};{node.brief};{signature};{args};\n')
            for include in includes:
                csv.write(include)
    else:
        with open(path_to_csv) as csv:
            cached_data = csv.read()
        cached_lines = cached_data.splitlines()[2:]
        cached_entities = {}
        for line in cached_lines:
            entity_data = line.split(';')
            name = entity_data[1]
            signature = entity_data[4]
            cached_entities[name + signature] = entity_data[2] # cache sections
        with open(path_to_csv, 'w') as csv:
            csv.write('sep=;\n')
            csv.write(f'{path_to_header};\n')
            for node in PreOrderIter(root):
                signature = node.signature.replace(node.name, node.entity_name)
                (name, signature, args) = postproc(node.entity_name, node.type, signature, node.args, excludes_post)
                if name + signature in cached_entities:
                    csv.write(f'{node.type};{name};{cached_entities[name + signature]};{node.brief};{signature};{args};\n')
                else:
                    csv.write(f'{node.type};{name};{topic};{node.brief};{signature};{args};\n')
            for include in includes:
                csv.write(include)



extracted_info_folder_name = 'extracted_info/'

def main():
    version = sys.argv[1]
    prefix = ''
    # prefix = '../'
    (sources, excluded_files, global_excludes, global_excludes_post, 
     files_excludes, files_excludes_post, files_includes, defined_symbols) = parse_conf(open(f'{prefix}source/{version}/api-doc/parse_conf.txt', 'r').read())
    for topic, src in sources.items():
        dest = prefix + 'source/' + version + '/api-doc/' + extracted_info_folder_name + topic
        for root_folder, dirs, files in os.walk(prefix + src):
            relative_root = root_folder.replace(prefix + src, '')
            csv_path = dest + '/'  + relative_root
            Path(csv_path).mkdir(exist_ok=True)
            for file in files:
                if (file.endswith('.h') or file.endswith('.hpp')) and file not in excluded_files:
                    header_full_name = root_folder.replace('\\', '/') + '/' + file
                    header_short_name = file
                    root.scope_start = 0
                    root.scope_end = sys.maxsize
                    root.stopped_at = 0
                    root.children = []
                    parse_code(open(header_full_name, 'r').read(), global_excludes + 
                            (files_excludes[header_short_name] if header_short_name in files_excludes else []), defined_symbols)
                    update_csv(f'{csv_path}/{header_short_name.rpartition('.')[0]}.csv', (files_includes[header_short_name] if header_short_name in files_includes
                                else []), global_excludes_post + (files_excludes_post[header_short_name] if header_short_name in files_excludes_post else []),
                                topic, header_full_name.replace('../NauEngine/', ''))

if __name__ == '__main__':
    main()
