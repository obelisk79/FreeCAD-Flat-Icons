#!/usr/bin/env python
"""
Optimize and build the qrc file.
copyright 2024 by Frank David Martinez M.
license: CCO-1.0
"""

import sys
from pathlib import Path
import shutil, os
import argparse
import re
import scour.scour
import textwrap

OPTIMIZER_AVAILABLE = True
try:
    import scour
    print(f"Optimization is available: scour-{scour.__version__}")
except:
    OPTIMIZER_AVAILABLE = False
    print("Optimization is disabled. Consider installing scour", file=sys.stderr)

SVG_PATTERN = re.compile(r'^.*\.svg$', re.IGNORECASE)

def optimize(src_dir: Path, icons_dir: Path, base_dir: Path):
    from scour import scour
    for root, dirs, files in os.walk(src_dir):
        path = Path(root).relative_to(base_dir)
        dest = icons_dir / path
        if not dest.exists():
            dest.mkdir(parents=True)
        for file in files:
            if SVG_PATTERN.fullmatch(file):
                with open(base_dir / path / file, 'r') as fin:
                    svg = scour.scourString(fin.read())
                    with open(dest / file, 'w') as fout:
                        fout.write(svg)
            else:
                shutil.copy(base_dir / path / file, dest / file)            


def build(icons_dir: Path, base_dir: Path):
    names = []
    for root, dirs, files in os.walk(icons_dir):
        path = Path(root).relative_to(base_dir)
        for file in files:
            names.append(f"<file>./{path / file}</file>\n")

    with open(base_dir / 'icons.qrc', 'w') as out:
        template = f"""\
        <RCC>
          <qresource>
            {"            ".join(sorted(names))}
          </qresource>
        </RCC>
        """
        out.write(textwrap.dedent(template))
        

def main(optimized: bool = True):
    base_dir = Path(__file__).parent
    src_dir = base_dir / "icons"
    if optimized:
        icons_dir = base_dir / "build"
        if icons_dir.exists():
            shutil.rmtree(icons_dir)
        icons_dir.mkdir()
        optimize(src_dir, icons_dir, base_dir)
    else:
        print("Optimization is disabled")
        icons_dir = src_dir
    build(icons_dir, base_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate .qrc file, optionally with optimized icons',
        epilog='A directory.qrc file will be generated in the current directory')
    parser.add_argument('--no-opt',
        help='Disables optimization', 
        default=False,
        action='store_true')    

    args = parser.parse_args()
    main(OPTIMIZER_AVAILABLE and (not args.no_opt))
