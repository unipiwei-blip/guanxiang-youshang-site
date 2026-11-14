# -*- coding: utf-8 -*-
"""一次性改版脚本：品牌锁定、去强制断行、取消窄行长内联限制。
可重复运行（幂等）。"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

BRAND_OLD = (
    '<span class="brand__text">\n'
    '        <span class="brand__name">莞香攸商</span>\n'
    '        <span class="brand__sub">东莞市湖南攸县商会</span>\n'
    '      </span>'
)

BRAND_RE = re.compile(
    r'<span class="brand__text">\s*'
    r'<span class="brand__name">莞香攸商</span>\s*'
    r'<span class="brand__sub">东莞市湖南攸县商会</span>\s*'
    r'</span>'
)

BRAND_NEW = (
    '<span class="brand__text">'
    '<span class="brand__name">东莞市湖南攸县商会</span>'
    '<span class="brand__sub">DONGGUAN YOUSHANG CHAMBER</span>'
    '</span>'
)

# 具体逐条替换（精确匹配，命中即换）
EXACT = [
    # h1 取消硬断行
    ('<h1>一间商会，<br>一群攸县人</h1>', '<h1>一间商会，一群攸县人</h1>'),
    ('<h1>把一个人的经验，<br>变成一群人的底气</h1>',
     '<h1>把一个人的经验，变成一群人的底气</h1>'),
    ('<h1>攸水贯境，<br>梅城千年</h1>', '<h1>攸水贯境，梅城千年</h1>'),
    ('<h1>一条班线，<br>把园区和东莞接上</h1>',
     '<h1>一条班线，把园区和东莞接上</h1>'),
    # 404 正文
    ('<p>你要找的页面可能已经迁移，或链接写错了。<br>回到首页重新走一遍，或直接去看商会最近做了什么。</p>',
     '<p>你要找的页面可能已经迁移，或链接写错了。回到首页重新走一遍，或直接去看商会最近做了什么。</p>'),
    # 图片角标改为一行
    ('<div class="home-figure__badge">酒仙湖<br>国家 4A 级旅游景区</div>',
     '<div class="home-figure__badge">酒仙湖 · 国家 4A 级旅游景区</div>'),
    # 入会两种方式：标签与说明合为一段
    ('<p><b>一、公众号留言</b><br>关注微信公众号',
     '<p><b>一、公众号留言</b> 关注微信公众号'),
    ('margin-top:6px"><b>二、到访会址</b><br>广东省东莞市寮步镇',
     'margin-top:6px"><b>二、到访会址</b> 广东省东莞市寮步镇'),
    # 联系页与两个首页段落的行长限制
    ('line-height:1.9;max-width:52em">', 'line-height:1.9">'),
    ('margin-top:12px;max-width:40ch">', 'margin-top:12px">'),
    ('margin-top:12px;max-width:44ch">', 'margin-top:12px">'),
    ('font-size:.84rem;color:var(--muted);max-width:26ch">',
     'font-size:.84rem;color:var(--muted)">'),
    # 品牌可读性
    ('alt="莞香攸商 商会标志"', 'alt="东莞市湖南攸县商会标志"'),
    ('aria-label="莞香攸商 首页"', 'aria-label="东莞市湖南攸县商会 首页"'),
]

targets = sorted(ROOT.glob('*.html')) + sorted(ROOT.glob('news/*.html'))
changed = {}

for f in targets:
    raw = f.read_text(encoding='utf-8')
    new = raw
    n_brand = 0
    def repl(m):
        global n_brand
        n_brand += 1
        return BRAND_NEW
    new, cnt = BRAND_RE.subn(BRAND_NEW, new)
    for old, rep in EXACT:
        if old in new:
            new = new.replace(old, rep)
    if new != raw:
        f.write_text(new, encoding='utf-8', newline='\n')
        changed[str(f.relative_to(ROOT))] = cnt

print('changed files:', len(changed))
for k, v in changed.items():
    print('  ', k, 'brand-lock:', v)
