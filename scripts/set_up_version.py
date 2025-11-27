# Copyright 2025 N-GINN LLC. All rights reserved.
# Use of this source code is governed by a BSD-3 Clause license that can be found in the LICENSE file.

import sys
import os
import shutil
import re

def main():
    base_version = sys.argv[1]
    version = sys.argv[2]
    prefix = ''

    # base_version = sys.argv[1].split(" ")[0]
    # version = sys.argv[1].split(" ")[1]
    # prefix = '../'

    destination = prefix + 'source/' + version
    source = prefix + 'source/' + base_version

    # Reset the directory to base.
    shutil.rmtree(destination, ignore_errors=True)
    os.makedirs(destination, exist_ok=True)
    for item in os.listdir(source):
        source_item = os.path.join(source, item)
        destination_item = os.path.join(destination, item)
        
        if os.path.isdir(source_item):
            shutil.copytree(source_item, destination_item)
        else:
            shutil.copy2(source_item, destination_item)

    # Fix paths html templates
    with open(destination + "/api-doc/_templates/user_link.html") as html:
        api_template = html.read()
        api_template = api_template.replace(f'href=\"/{base_version}/user-doc/index.html\"', 
                         f'href=\"/{version}/user-doc/index.html\"')
    open(destination + "/api-doc/_templates/user_link.html", 'w').write(api_template)

    with open(destination + "/user-doc/_templates/api_link.html") as html:
        user_template = html.read()
        user_template = user_template.replace(f'href=\"/{base_version}/api-doc/index.html\"', 
                          f'href=\"/{version}/api-doc/index.html\"')
    open(destination + "/user-doc/_templates/api_link.html", 'w').write(user_template)

    # Change doxygen output directory
    doxyfile_full_name = destination + '/api-doc/Doxyfile'

    sub = 'OUTPUT_DIRECTORY       = ' + destination + '/api-doc'
    source_dir_pattern = re.compile(r'^OUTPUT_DIRECTORY       = [^\n]+', re.MULTILINE)
    
    with open(doxyfile_full_name, 'r') as doxyfile:
        config = doxyfile.read()
    config = source_dir_pattern.sub(sub, config)
    with open(doxyfile_full_name, 'w') as doxyfile:
        doxyfile.write(config)

    link_prefix_pattern = re.compile(fr'^api_link_prefix = [^\n]+', re.MULTILINE)
    new_link_prefix = f'api_link_prefix = \'/{version}/api-doc/generated_content/\''
    conf_full_name = destination + '/user-doc/conf.py'
    with open(conf_full_name, 'r') as conf:
        conf_text = conf.read()
    conf_text = link_prefix_pattern.sub(new_link_prefix, conf_text)
    with open(conf_full_name, 'w') as conf:
        conf.write(conf_text)
if __name__ == '__main__':
    main()
