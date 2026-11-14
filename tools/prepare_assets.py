# -*- coding: utf-8 -*-
"""生成站点所需的图片素材：处理 LOGO、下载场景图、生成分享图与 favicon。
运行：python tools/prepare_assets.py
"""
import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(IMG, exist_ok=True)

SOURCES = {
    "dongguan.jpg": "https://aka.doubaocdn.com/s/DNxIO4oE24",
    "youxian-lake.jpg": "https://aka.doubaocdn.com/s/53MnA1ZCmz",
    "xianggan.jpg": "https://aka.doubaocdn.com/s/V3Z8z4KizX",
    "office.jpg": "https://aka.doubaocdn.com/s/hm2UVFk788",
}


def download(url, dest, max_w=1800, quality=82):
    if os.path.exists(dest):
        print("skip", dest)
        return
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    tmp = dest + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    im = Image.open(tmp).convert("RGB")
    if im.width > max_w:
        h = int(im.height * max_w / im.width)
        im = im.resize((max_w, h), Image.LANCZOS)
    im.save(dest, "JPEG", quality=quality, optimize=True, progressive=True)
    os.remove(tmp)
    print("ok", dest, im.size)


def strip_white(path, out, size=640, near=250, fade=236):
    im = Image.open(path).convert("RGBA")
    im = im.crop(im.convert("RGB").point(lambda p: p).getbbox())
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            lum = min(r, g, b)
            if lum >= near:
                px[x, y] = (r, g, b, 0)
            elif lum >= fade:
                px[x, y] = (r, g, b, int(255 * (near - lum) / (near - fade)))
    side = max(w, h)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(im, ((side - w) // 2, (side - h) // 2), im)
    canvas = canvas.resize((size, size), Image.LANCZOS)
    canvas.save(out, "PNG", optimize=True)
    print("logo", out, canvas.size)


def font(size, bold=True):
    for name in (("msyhbd.ttc", "msyh.ttc") if bold else ("msyh.ttc",)):
        p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def og_card(logo_path, out):
    W, H = 1200, 630
    bg = Image.new("RGB", (W, H), "#FFFFFF")
    d = ImageDraw.Draw(bg)
    # 点阵底纹
    for y in range(24, H, 28):
        for x in range(24, W, 28):
            d.point((x, y), fill="#E8EDF1")
    # 右侧留白处的同心细圆，只做边缘装饰，不压文字
    for r in (300, 232, 164):
        d.ellipse((1150 - r, 300 - r, 1150 + r, 300 + r), outline="#F1DAD5", width=2)
    logo = Image.open(logo_path).convert("RGBA")
    logo.thumbnail((270, 270), Image.LANCZOS)
    bg.paste(logo, (78, (H - 12 - logo.height) // 2), logo)
    x = 430
    d.text((x, 150), "DONGGUAN  ·  HUNAN  ·  YOUXIAN", font=font(22, False), fill="#B3160E")
    d.text((x, 194), "东莞市湖南攸县商会", font=font(58), fill="#0E1B26")
    d.line((x, 300, x + 96, 300), fill="#E2231A", width=4)
    d.text((x, 330), "联络乡情 · 服务企业 · 融通莞攸", font=font(28, False), fill="#33434F")
    d.text((x, 396), "2015 年登记成立 · 东莞市寮步镇松湖智谷", font=font(22, False), fill="#8A97A2")
    d.rectangle((0, H - 12, W, H), fill="#E2231A")
    bg.save(out, "JPEG", quality=88, optimize=True)
    print("og", out)


if __name__ == "__main__":
    for name, url in SOURCES.items():
        download(url, os.path.join(IMG, name))
    logo_src = os.path.join(ASSETS, "logo-original.jpg")
    logo_png = os.path.join(ASSETS, "logo.png")
    strip_white(logo_src, logo_png, size=480)
    strip_white(logo_src, os.path.join(ASSETS, "logo-mark.png"), size=256)
    strip_white(logo_src, os.path.join(ASSETS, "favicon-64.png"), size=64)
    strip_white(logo_src, os.path.join(ASSETS, "apple-touch-icon.png"), size=180)
    og_card(logo_png, os.path.join(IMG, "og-cover.jpg"))
