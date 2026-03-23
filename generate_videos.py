#!/usr/bin/env python3
"""
ワイン教育ショート動画 生成スクリプト
- gTTS で日本語音声生成
- Pillow でテキストフレーム生成
- moviepy で映像+音声を合成
"""

import os
import re
import textwrap
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import AudioFileClip, ImageClip, concatenate_videoclips

# ---------------------------------------------------------------------------
# 設定
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 1080, 1920   # 縦型ショート動画 (9:16)
FPS = 30
FONT_PATH = "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"
OUTPUT_DIR = Path("output_videos")
OUTPUT_DIR.mkdir(exist_ok=True)

# カラーテーマ（ワイン系）
BG_COLOR       = (30, 10, 20)        # 深い紫黒
ACCENT_COLOR   = (180, 30, 60)       # ワインレッド
HIGHLIGHT_COLOR= (240, 200, 100)     # ゴールド
TEXT_COLOR     = (245, 235, 230)     # クリーム白
SUB_TEXT_COLOR = (180, 160, 155)     # グレー系

# ---------------------------------------------------------------------------
# 動画コンテンツ定義
# ---------------------------------------------------------------------------
VIDEOS = [
    {
        "id": "01",
        "title": "ワインって結局\n何種類あるの？",
        "scenes": [
            {
                "text": "ワインって赤・白・ロゼ\n以外にもあるって知ってた？",
                "narration": "ワインって赤、白、ロゼ以外にもあるって知ってた？",
                "duration": 5,
                "is_hook": True,
            },
            {
                "text": "ワインは大きく分けて\n【5種類】",
                "narration": "ワインは大きく分けて5種類。",
                "duration": 3,
                "highlight": True,
            },
            {
                "text": "🍷 赤ワイン\n黒ブドウを皮ごと発酵\n→ 渋みと深みが特徴",
                "narration": "まず赤ワイン。黒ブドウを皮ごと発酵させたもの。渋みと深みが特徴。",
                "duration": 5,
            },
            {
                "text": "🥂 白ワイン\n果汁だけ発酵\n→ すっきり爽やか",
                "narration": "次に白ワイン。主に白ブドウを果汁だけ発酵させたもの。すっきり爽やか。",
                "duration": 5,
            },
            {
                "text": "🌸 ロゼ\n赤と白の中間\n→ フルーティーで飲みやすい",
                "narration": "ロゼは赤と白の中間。色がきれいでフルーティー。",
                "duration": 4,
            },
            {
                "text": "✨ スパークリング\nシャンパンはその中のひとつ\nシャンパン ⊂ スパークリング",
                "narration": "スパークリングは発泡してるやつ全般。シャンパンはその中のひとつ。",
                "duration": 5,
            },
            {
                "text": "🍯 デザートワイン\n食後にちびちび飲む\n濃くて甘いやつ",
                "narration": "最後にデザートワイン。食後にちびちび飲む、濃くて甘いやつ。",
                "duration": 4,
            },
            {
                "text": "この5つを知るだけで\nワイン選びが\n一気に楽になる！",
                "narration": "この5つを知っているだけで、レストランでのワイン選びが一気に楽になるよ。フォローして待っててね！",
                "duration": 6,
                "is_outro": True,
            },
        ],
    },
    {
        "id": "02",
        "title": "タンニンって何？\n渋みの正体",
        "scenes": [
            {
                "text": "赤ワインが渋い理由\nちゃんと説明できる？",
                "narration": "赤ワインが渋い理由、ちゃんと説明できる？",
                "duration": 4,
                "is_hook": True,
            },
            {
                "text": "渋みの正体は\n【タンニン】\nポリフェノールの一種",
                "narration": "赤ワインの渋みの正体はタンニンというポリフェノールの一種。",
                "duration": 5,
                "highlight": True,
            },
            {
                "text": "ブドウの皮・種・茎に含まれる\n↓\n皮ごと発酵 → 渋みが出る",
                "narration": "ブドウの皮、種、茎に含まれていて、赤ワインは皮ごと発酵させるから渋みが出る。",
                "duration": 5,
            },
            {
                "text": "タンニン × 口の中のたんぱく質\n→ パサっとした感覚が生まれる",
                "narration": "タンニンは口の中のたんぱく質と結びついて、あのパサっとした感覚を作り出している。",
                "duration": 5,
            },
            {
                "text": "渋みが苦手な人に朗報！\n\n肉料理と合わせると\n渋みが消える✨",
                "narration": "渋みが苦手な人に朗報。タンニンの多いワインは肉料理と合わせると渋みが消えるんだよ。",
                "duration": 6,
                "highlight": True,
            },
            {
                "text": "タンニン少なめの赤ワインなら\n【ピノ・ノワール】\nがおすすめ！",
                "narration": "タンニン少なめの赤ワインが飲みたい人は、ピノ・ノワールって書いてあるのを探してみて。すごく飲みやすいよ。",
                "duration": 6,
                "is_outro": True,
            },
        ],
    },
    {
        "id": "03",
        "title": "ワインのラベル\nどこ見ればいい？",
        "scenes": [
            {
                "text": "ワインのラベル\n何が書いてあるか\nわからないよね",
                "narration": "ワインのラベル、正直何が書いてあるかわからないよね。3つだけ見てみて。",
                "duration": 5,
                "is_hook": True,
            },
            {
                "text": "見るべきポイントは\n【3つだけ】",
                "narration": "ラベルで見るべきポイントは3つだけ。",
                "duration": 3,
                "highlight": True,
            },
            {
                "text": "① 生産国\nフランス・イタリア → やや渋め\nチリ・オーストラリア → 飲みやすい",
                "narration": "1つ目は生産国。フランス・イタリア・スペインはやや渋め。チリ・オーストラリア・アメリカはフルーティーで飲みやすい。",
                "duration": 7,
            },
            {
                "text": "② ブドウ品種\n白：シャルドネ（濃厚）\n   ソーヴィニョン・ブラン（爽やか）",
                "narration": "2つ目はブドウ品種。白ならシャルドネは濃厚、ソーヴィニョン・ブランはさっぱり。",
                "duration": 6,
            },
            {
                "text": "② ブドウ品種\n赤：カベルネ（しっかり）\n   ピノ・ノワール（軽やか）",
                "narration": "赤ならカベルネ・ソーヴィニョンはしっかり、ピノ・ノワールは軽やか。",
                "duration": 5,
            },
            {
                "text": "③ 価格帯\n1000〜2000円でも\n十分おいしいワインが山ほどある",
                "narration": "3つ目は価格帯。1000円から2000円でも十分おいしいワインは山ほどある。高ければいいわけじゃない。",
                "duration": 6,
            },
            {
                "text": "初心者にまずおすすめ\n→【チリワイン】\nコスパ最強で飲みやすい！",
                "narration": "初心者にまずおすすめしたいのはチリワイン。コスパ最強で飲みやすいのが多いから、ぜひ試してみて。",
                "duration": 6,
                "is_outro": True,
            },
        ],
    },
]

# ---------------------------------------------------------------------------
# ヘルパー関数
# ---------------------------------------------------------------------------

def make_frame(text: str, scene: dict, video_meta: dict) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # 背景グラデーション風（上部と下部に帯）
    for y in range(200):
        alpha = int(80 * (1 - y / 200))
        draw.line([(0, y), (WIDTH, y)], fill=tuple(max(0, c - alpha) for c in BG_COLOR))

    # フック画面の強調背景
    if scene.get("is_hook"):
        draw.rectangle([(0, HEIGHT // 3), (WIDTH, HEIGHT * 2 // 3)], fill=(50, 15, 30))

    # アウトロの背景
    if scene.get("is_outro"):
        draw.rectangle([(40, HEIGHT // 4), (WIDTH - 40, HEIGHT * 3 // 4)],
                       outline=ACCENT_COLOR, width=4)

    # ハイライト強調の場合は背景帯
    if scene.get("highlight"):
        draw.rectangle([(60, HEIGHT // 3 - 20), (WIDTH - 60, HEIGHT * 2 // 3 + 20)],
                       fill=(60, 10, 30))

    # タイトル（上部）
    try:
        title_font = ImageFont.truetype(FONT_PATH, 52)
    except Exception:
        title_font = ImageFont.load_default()

    title_lines = video_meta["title"].split("\n")
    ty = 120
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        draw.text(((WIDTH - tw) // 2, ty), line, font=title_font, fill=ACCENT_COLOR)
        ty += 65

    # 区切り線
    draw.line([(80, ty + 10), (WIDTH - 80, ty + 10)], fill=ACCENT_COLOR, width=2)

    # メインテキスト（中央）
    try:
        main_font_size = 72 if scene.get("highlight") else 64
        main_font = ImageFont.truetype(FONT_PATH, main_font_size)
    except Exception:
        main_font = ImageFont.load_default()

    lines = text.split("\n")
    total_height = len(lines) * (main_font_size + 20)
    start_y = (HEIGHT - total_height) // 2

    for i, line in enumerate(lines):
        # 先頭が【】で囲まれた強調テキスト
        if line.startswith("【") and "】" in line:
            color = HIGHLIGHT_COLOR
            try:
                f = ImageFont.truetype(FONT_PATH, main_font_size + 10)
            except Exception:
                f = main_font
        elif line.startswith("→") or line.startswith("↓"):
            color = HIGHLIGHT_COLOR
            f = main_font
        else:
            color = TEXT_COLOR
            f = main_font

        bbox = draw.textbbox((0, 0), line, font=f)
        lw = bbox[2] - bbox[0]
        x = (WIDTH - lw) // 2
        y = start_y + i * (main_font_size + 20)
        draw.text((x, y), line, font=f, fill=color)

    # 動画番号バッジ（右下）
    try:
        badge_font = ImageFont.truetype(FONT_PATH, 36)
    except Exception:
        badge_font = ImageFont.load_default()

    badge = f"#{video_meta['id']}"
    draw.text((WIDTH - 100, HEIGHT - 80), badge, font=badge_font, fill=SUB_TEXT_COLOR)

    return img


def generate_bgm(duration: float, path: str, base_freq: float = 220.0):
    """ワイン風のおしゃれなBGMをオフラインで生成（サイン波コード）"""
    import wave, struct, numpy as np

    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)

    # Am7コード風（A-C-E-G）
    freqs = [base_freq, base_freq * 6/5, base_freq * 3/2, base_freq * 7/4]
    wave_data = np.zeros(n_samples)
    for freq in freqs:
        wave_data += 0.15 * np.sin(2 * np.pi * freq * t)
        wave_data += 0.05 * np.sin(2 * np.pi * freq * 2 * t)  # 倍音

    # フェードイン・フェードアウト
    fade = int(sample_rate * 0.3)
    wave_data[:fade] *= np.linspace(0, 1, fade)
    wave_data[-fade:] *= np.linspace(1, 0, fade)

    # 正規化
    wave_data = (wave_data / np.max(np.abs(wave_data)) * 32767 * 0.6).astype(np.int16)

    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(wave_data.tobytes())


def build_video(video_meta: dict):
    vid_id = video_meta["id"]
    print(f"\n[{vid_id}] 動画生成開始: {video_meta['title'].replace(chr(10), ' ')}")

    clips = []
    tmp_dir = OUTPUT_DIR / f"tmp_{vid_id}"
    tmp_dir.mkdir(exist_ok=True)

    for i, scene in enumerate(video_meta["scenes"]):
        print(f"  シーン {i+1}/{len(video_meta['scenes'])}: {scene['text'][:20]}...")

        # フレーム画像生成
        img = make_frame(scene["text"], scene, video_meta)
        img_path = str(tmp_dir / f"scene_{i:02d}.png")
        img.save(img_path)

        # BGM生成（オフライン）
        audio_path = str(tmp_dir / f"audio_{i:02d}.wav")
        duration = scene["duration"]
        generate_bgm(duration, audio_path)
        audio_clip = AudioFileClip(audio_path)

        # 映像クリップ作成
        img_clip = ImageClip(img_path, duration=duration)
        img_clip = img_clip.with_audio(audio_clip)
        clips.append(img_clip)

    # 結合して書き出し
    final = concatenate_videoclips(clips, method="compose")
    out_path = str(OUTPUT_DIR / f"wine_{vid_id}.mp4")
    final.write_videofile(
        out_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        logger=None,
    )
    print(f"  完了 → {out_path}  ({final.duration:.1f}秒)")

    # クリーンアップ
    for f in tmp_dir.iterdir():
        f.unlink()
    tmp_dir.rmdir()

    return out_path


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== ワイン教育ショート動画 生成開始 ===")
    generated = []
    for video in VIDEOS:
        path = build_video(video)
        generated.append(path)

    print("\n=== 生成完了 ===")
    for p in generated:
        size_mb = os.path.getsize(p) / 1024 / 1024
        print(f"  {p}  ({size_mb:.1f} MB)")
