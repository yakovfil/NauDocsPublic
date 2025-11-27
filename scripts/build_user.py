# Copyright 2025 N-GINN LLC. All rights reserved.
# Use of this source code is governed by a BSD-3 Clause license that can be found in the LICENSE file.

import sys
import subprocess

def main():
    version = sys.argv[1]
    source_dir = f'source/{version}/user-doc'
    build_dir = f'build/{version}/user-doc'
    subprocess.run(["sphinx-build", source_dir, build_dir])

if __name__ == '__main__':
    main()
