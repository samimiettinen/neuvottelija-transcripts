import json
import os
import subprocess
import sys
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "transcript_config.json"
OUTPUT_DIR = ROOT / "output"
AUDIO_DIR = ROOT / "audio"


def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config not found: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def download_audio(youtube_url: str, out_basename: str) -> Path:
    AUDIO_DIR.mkdir(exist_ok=True)
    out_path = AUDIO_DIR / f"{out_basename}.mp3"
    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "-o", str(out_path),
        youtube_url,
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    return out_path


def transcribe_to_srt(client: OpenAI, audio_path: Path, model: str, language: str, out_basename: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    srt_path = OUTPUT_DIR / f"{out_basename}.srt"

    with open(audio_path, "rb") as f:
        print(f"Transcribing {audio_path} -> {srt_path}")
        transcript = client.audio.transcriptions.create(
            model=model,
            file=f,
            response_format="srt",
            language=language,
        )

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(transcript)
    return srt_path


def main():
    cfg = load_config()
    youtube_url = cfg["youtube_url"]
    out_basename = cfg.get("output_basename", "output")
    model = cfg.get("model", "whisper-1")
    language = cfg.get("language", "fi")
    api_key = cfg.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing (env or transcript_config.json).")

    client = OpenAI(api_key=api_key)

    audio_path = download_audio(youtube_url, out_basename)
    srt_path = transcribe_to_srt(client, audio_path, model, language, out_basename)

    print(f"\nDone. Upload this file to YouTube subtitles (With timing): {srt_path}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print("Error running external command:", e, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)
