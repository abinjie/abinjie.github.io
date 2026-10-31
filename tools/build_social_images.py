#!/usr/bin/env python3
"""Render checked-in sharing cards. Optional authoring dependency: Pillow.

Normal site builds use the existing PNGs and need only Python's standard library.
Pass --sans-font, --serif-font and --mono-font when using other CJK fonts.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'assets/social'
PAPER, INK, GREEN = '#f7f7f2', '#1e3029', '#285b49'
MUTED, LINE, PALE = '#5e6b61', '#d8ded2', '#e9eedf'


def font_path(requested, candidates):
    if requested:
        path = Path(requested)
        if path.is_file():
            return str(path)
        raise SystemExit(f'Font not found: {path}')
    for candidate in candidates:
        if Path(candidate).is_file():
            return candidate
    raise SystemExit('CJK fonts unavailable. Supply explicit font paths; see --help.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for family in ('sans', 'serif', 'mono'):
        parser.add_argument(f'--{family}-font')
    args = parser.parse_args()
    sans = font_path(args.sans_font, ['/System/Library/Fonts/STHeiti Light.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'])
    serif = font_path(args.serif_font, ['/System/Library/Fonts/Supplemental/Songti.ttc', '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'])
    mono = font_path(args.mono_font, ['/System/Library/Fonts/SFNSMono.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'])
    OUTPUT.mkdir(parents=True, exist_ok=True)

    def card(label):
        canvas = Image.new('RGBA', (1200, 630), PAPER)
        draw = ImageDraw.Draw(canvas)
        draw.text((64, 48), 'b.', font=ImageFont.truetype(serif, 52), fill=INK)
        draw.text((145, 60), 'BINJIE', font=ImageFont.truetype(mono, 25), fill=INK)
        draw.text((145, 94), 'ROBOTICS & SIMULATION', font=ImageFont.truetype(mono, 12), fill=MUTED)
        draw.text((822, 74), label, font=ImageFont.truetype(mono, 17), fill=GREEN)
        draw.line((64, 133, 1136, 133), fill=LINE, width=1)
        draw.line((64, 558, 1136, 558), fill=LINE, width=1)
        draw.text((64, 582), 'abinjie.github.io', font=ImageFont.truetype(mono, 19), fill=MUTED)
        draw.text((825, 584), 'SIMULATION → REALITY', font=ImageFont.truetype(mono, 17), fill=GREEN)
        return canvas, draw

    home, draw = card('ENGINEERING / NOTES')
    draw.text((64, 175), '你好，我是宾杰。', font=ImageFont.truetype(serif, 36), fill=INK)
    draw.text((64, 238), '在仿真中，', font=ImageFont.truetype(serif, 64), fill=INK)
    draw.text((64, 320), '走向真实世界。', font=ImageFont.truetype(serif, 64), fill=GREEN)
    draw.text((68, 432), '机器人工程师 · 仿真与算法', font=ImageFont.truetype(sans, 26), fill=INK)
    draw.text((68, 481), 'Isaac Sim / MuJoCo / Sim2Real', font=ImageFont.truetype(mono, 19), fill=MUTED)
    draw.ellipse((754, 179, 1121, 519), outline=LINE, width=2)
    arm = Image.open(ROOT / 'assets/media/robotics-manipulator-cutout.webp').convert('RGBA')
    arm.thumbnail((430, 430), Image.Resampling.LANCZOS)
    home.alpha_composite(arm, (716, 139))
    home.convert('RGB').save(OUTPUT / 'home.png', optimize=True)

    project, draw = card('PROJECT / ROBOARENA')
    draw.text((64, 192), 'RoboArena', font=ImageFont.truetype(sans, 65), fill=INK)
    draw.text((66, 289), '机器人模型测评平台', font=ImageFont.truetype(serif, 40), fill=GREEN)
    draw.text((68, 393), '本地物理仿真 · 云端视觉渲染', font=ImageFont.truetype(sans, 24), fill=MUTED)
    draw.text((68, 437), 'VLA 推理 · 机器人控制', font=ImageFont.truetype(sans, 24), fill=MUTED)
    for x, y, location, title, stack in [
        (716, 180, 'LOCAL / 01', '物理仿真', 'Isaac Sim'),
        (936, 180, 'CLOUD / 02', '视觉渲染', '3DGS'),
        (716, 339, 'CLOUD / 03', '模型推理', 'VLA'),
        (936, 339, 'LOCAL / 04', '控制执行', 'Controller'),
    ]:
        draw.rectangle((x, y, x + 200, y + 137), fill=PALE, outline=LINE, width=1)
        draw.text((x + 18, y + 17), location, font=ImageFont.truetype(mono, 13), fill=GREEN)
        draw.text((x + 18, y + 49), title, font=ImageFont.truetype(sans, 25), fill=INK)
        draw.text((x + 18, y + 94), stack, font=ImageFont.truetype(mono, 17), fill=MUTED)
    draw.text((718, 502), '01 → 02 → 03 → 04 → 01', font=ImageFont.truetype(mono, 18), fill=GREEN)
    project.convert('RGB').save(OUTPUT / 'roboarena.png', optimize=True)
    print('Rendered 2 sharing cards (1200 × 630).')


if __name__ == '__main__':
    main()
