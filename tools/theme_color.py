# -*- coding: utf-8 -*-
"""把 theme-color 与 404 内联变量同步到浅色主题。"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
files = sorted(ROOT.glob('*.html')) + sorted(ROOT.glob('news/*.html'))
n = 0
for f in files:
    s = f.read_text(encoding='utf-8')
    o = s
    s = s.replace('content="#100d0c"', 'content="#ffffff"')
    s = s.replace('--ink: #100d0c;', '--ink: #0e1b26;')
    if s != o:
        f.write_text(s, encoding='utf-8', newline='\n')
        n += 1
print('theme-color files:', n)
