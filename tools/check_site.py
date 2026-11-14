#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""站点自检脚本：内链、资源、结构、SEO 基本项、CSS 类名覆盖。

用法：python tools/check_site.py
退出码 0 表示无错误（警告不影响退出码）。
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}
TOKEN = "__SITE_DOMAIN__"


def site_prefix() -> str:
    """当前生效的站点根地址；未替换时仍是占位符。"""
    base_file = ROOT / ".site-base"
    if base_file.exists():
        value = base_file.read_text(encoding="utf-8").strip()
        if value:
            return value
    return TOKEN


PREFIX = site_prefix()

errors: list[str] = []
warnings: list[str] = []


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, int]] = []
        self.refs: list[tuple[str, str, int]] = []   # (tag, value, line)
        self.classes: set[str] = set()
        self.ids: list[tuple[str, int]] = []
        self.head_tags: dict[str, list[str]] = {}
        self.jsonld: list[str] = []
        self._in_jsonld = False
        self._jsonld_buf: list[str] = []
        self._in_head = False
        self.h1 = 0
        self.title = False
        self.lang = ""

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        a = {k: (v or "") for k, v in attrs}
        if tag == "html":
            self.lang = a.get("lang", "")
        if tag == "head":
            self._in_head = True
        if tag == "body":
            self._in_head = False
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self.title = True
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_jsonld = True
            self._jsonld_buf = []
        if a.get("class"):
            for c in a["class"].split():
                self.classes.add(c)
        if a.get("id"):
            self.ids.append((a["id"], line))
        for key in ("href", "src"):
            if key in a and a[key]:
                self.refs.append((key, a[key], line))
        if self._in_head:
            for key in ("name", "property", "rel"):
                if key in a:
                    self.head_tags.setdefault(f"{key}:{a[key]}", []).append(tag)
        if tag not in VOID:
            self.stack.append((tag, line))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag == "script" and self._in_jsonld:
            self._in_jsonld = False
            self.jsonld.append("\n".join(self._jsonld_buf))
            if self.stack and self.stack[-1][0] == "script":
                self.stack.pop()
            return
        if tag == "head":
            self._in_head = False
        if not self.stack:
            errors.append(f"多余的结束标签 </{tag}> 行 {self.getpos()[0]}")
            return
        if self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            # 容忍段落自动闭合一类的情况
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag:
                    opened = [t for t, _ in self.stack[i + 1:]]
                    if any(t not in {"p", "li", "td", "th", "tr"} for t in opened):
                        errors.append(
                            f"标签未闭合：</{tag}> 行 {self.getpos()[0]}，"
                            f"仍打开 {self.stack[-1][0]}（行 {self.stack[-1][1]}）"
                        )
                    del self.stack[i:]
                    return
            errors.append(f"找不到开标签的 </{tag}> 行 {self.getpos()[0]}")

    def handle_data(self, data):
        if self._in_jsonld:
            self._jsonld_buf.append(data)


def collect_css_classes() -> set[str]:
    css = (ROOT / "css" / "style.css").read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return set(re.findall(r"\.([a-zA-Z_][\w-]*)", css))


def check_page(path: Path, css_classes: set[str]) -> None:
    rel = path.relative_to(ROOT).as_posix()
    p = PageParser()
    p.feed(path.read_text(encoding="utf-8"))
    p.close()

    if p.stack:
        errors.append(f"{rel}: 有未闭合标签 {[t for t, _ in p.stack]}")

    # 内链与资源
    for key, value, line in p.refs:
        if value.startswith(("http://", "https://", "mailto:", "tel:", "#", "javascript:", "data:")) or TOKEN in value:
            if value.startswith("#") and len(value) > 1:
                target = value[1:]
                if target not in {i for i, _ in p.ids}:
                    errors.append(f"{rel}:{line} 页内锚点 #{target} 不存在")
            continue
        if value.startswith("/"):
            target = (ROOT / value.lstrip("/").split("#")[0].split("?")[0]).resolve()
        else:
            target = (path.parent / value.split("#")[0].split("?")[0]).resolve()
        if not target.exists():
            errors.append(f"{rel}:{line} 引用的本地文件不存在 → {value}")

    # 结构
    if p.h1 != 1:
        errors.append(f"{rel}: h1 数量应为 1，实际 {p.h1}")
    if not p.title:
        errors.append(f"{rel}: 缺少 <title>")
    if p.lang != "zh-CN":
        warnings.append(f"{rel}: html lang = {p.lang!r}")
    dup = [i for i in {i for i, _ in p.ids} if [x for x, _ in p.ids].count(i) > 1]
    if dup:
        errors.append(f"{rel}: id 重复 → {dup}")

    # SEO 头（404 为自包含单页 + noindex，不参与本项）
    if path.name != "404.html":
        need = ["name:description", "name:viewport", "rel:canonical", "property:og:title",
                "property:og:description", "property:og:url", "property:og:image", "rel:icon"]
        for key in need:
            if key not in p.head_tags:
                (errors if key != "rel:icon" else warnings).append(f"{rel}: 缺少 {key}")

    if "noindex" in "".join(p.head_tags.get("name:robots", [])):
        pass

    # JSON-LD
    for raw in p.jsonld:
        try:
            json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{rel}: JSON-LD 解析失败 → {exc}")

    # class 覆盖（仅提示；404 为自包含内联样式，不参与）
    if path.name != "404.html":
        for c in sorted(p.classes - css_classes):
            warnings.append(f"{rel}: class .{c} 未在 style.css 中定义")

    # 占位符 / 站点根地址（404 无需）
    text = path.read_text(encoding="utf-8")
    if path.name != "404.html" and PREFIX not in text and TOKEN not in text:
        warnings.append(f"{rel}: 未包含站点根地址（{PREFIX}）")


def main() -> int:
    css_classes = collect_css_classes()
    pages = sorted(ROOT.glob("*.html")) + sorted((ROOT / "news").glob("*.html"))
    for page in pages:
        check_page(page, css_classes)

    # sitemap
    sm = ROOT / "sitemap.xml"
    try:
        tree = ET.parse(sm)
        locs = [e.text for e in tree.getroot().iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    except ET.ParseError as exc:
        errors.append(f"sitemap.xml 解析失败 → {exc}")
        locs = []
    for loc in locs:
        if not loc:
            errors.append("sitemap.xml: 存在空的 loc")
            continue
        prefix = next((p for p in (PREFIX, TOKEN) if loc.startswith(p + "/")), None)
        if not prefix:
            errors.append(f"sitemap.xml: loc 未使用站点根地址 → {loc}")
            continue
        rel = loc[len(prefix) + 1:] or "index.html"
        if not (ROOT / rel).exists():
            errors.append(f"sitemap.xml: 指向的页面不存在 → {loc}")
    listed = set()
    for loc in locs:
        prefix = next((p for p in (PREFIX, TOKEN) if loc and loc.startswith(p + "/")), None)
        if prefix:
            rel = loc[len(prefix) + 1:] or "index.html"
            listed.add(rel)
    for page in pages:
        rel = page.relative_to(ROOT).as_posix()
        if rel == "404.html":
            continue
        if rel not in listed:
            warnings.append(f"sitemap.xml: 未收录 {rel}")

    # robots
    rb = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if PREFIX not in rb and TOKEN not in rb:
        errors.append("robots.txt: Sitemap 地址未使用站点根地址")

    # js 选择器在页面中的存在性（404 为自包含页面，不加载 main.js）
    js = (ROOT / "js" / "main.js").read_text(encoding="utf-8")
    checks = {
        ".scroll-line": "scroll-line",
        ".drawer": "drawer",
        ".burger": "burger",
        ".toast": "toast",
    }
    for page in pages:
        if page.name == "404.html":
            continue
        text = page.read_text(encoding="utf-8")
        for sel, cls in checks.items():
            if sel not in js:
                errors.append(f"main.js 中缺少选择器 {sel}")
            if f'class="{cls}"' not in text and f'"{cls}"' not in text:
                errors.append(f"{page.name}: 缺少 .{cls}，与 main.js 契约不符")
        if "heroCanvas" in text and 'id="heroCanvas"' not in text:
            errors.append(f"{page.name}: 提到 heroCanvas 但元素不存在")

    print(f"检查页面 {len(pages)} 个，sitemap 条目 {len(locs)} 条\n")
    for e in errors:
        print("ERROR  " + e)
    for w in warnings:
        print("WARN   " + w)
    print(f"\n结果：{len(errors)} 个错误，{len(warnings)} 个提示")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
