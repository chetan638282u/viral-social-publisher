from pathlib import Path
import textwrap
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def create_text_image(title: str, output_dir: Path) -> str:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "post.png"

    width, height = 1080, 1080
    image = Image.new("RGB", (width, height), "#101820")
    draw = ImageDraw.Draw(image)

    accent = "#FEE715"
    white = "#FFFFFF"
    muted = "#B7C2CC"

    draw.rectangle((0, 0, width, 140), fill=accent)
    draw.text((60, 44), "DAILY TECH SIGNAL", fill="#101820", font=_font(42, bold=True))

    wrapped = textwrap.wrap(title, width=24)
    y = 250
    for line in wrapped[:7]:
        draw.text((70, y), line, fill=white, font=_font(62, bold=True))
        y += 78

    draw.line((70, 850, 1010, 850), fill=accent, width=6)
    draw.text((70, 885), "Verified sources. Human approval before posting.", fill=muted, font=_font(30))

    image.save(path, quality=95)
    return str(path)


def create_original_audio(output_dir: Path, duration_seconds: int = 25) -> str:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "original_beat.wav"
    sample_rate = 44100
    timeline = np.linspace(0, duration_seconds, sample_rate * duration_seconds, endpoint=False)

    kick = 0.45 * np.sin(2 * np.pi * 55 * timeline) * ((timeline * 2) % 1 < 0.12)
    bass = 0.18 * np.sin(2 * np.pi * 110 * timeline)
    lead = 0.12 * np.sin(2 * np.pi * 440 * timeline) * (((timeline * 4).astype(int) % 4) == 0)
    audio = kick + bass + lead
    audio = np.clip(audio, -1, 1)
    pcm = (audio * 32767).astype(np.int16)

    with wave.open(str(path), "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(sample_rate)
        file.writeframes(pcm.tobytes())

    return str(path)


def create_short_video(
    image_path: str,
    audio_path: str,
    output_dir: Path,
    duration_seconds: int = 25,
    filename: str = "short_video.mp4",
) -> str:
    from moviepy.editor import AudioFileClip, ImageClip

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    clip = ImageClip(image_path).set_duration(duration_seconds).resize(height=1920).crop(width=1080, height=1920)
    audio = AudioFileClip(audio_path).subclip(0, duration_seconds)
    clip = clip.set_audio(audio)
    clip.write_videofile(str(path), fps=30, codec="libx264", audio_codec="aac", verbose=False, logger=None)
    audio.close()
    clip.close()
    return str(path)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()
