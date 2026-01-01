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
        sys.executable, "-m", "yt_dlp",
        "-x",
        "--audio-format", "mp3",
        "-o", str(out_path),
        youtube_url,
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    return out_path


def fix_whisper_timestamps(srt_content: str) -> str:
    """
    Fixes malformed timestamps from Whisper where the range separator might be a period instead of comma.
    Converts: 00:00:00.000.00:00:08.000 -> 00:00:00.000,00:00:08.000
    """
    import re
    # Pattern to match timestamp ranges with period separator (incorrect)
    # Matches: HH:MM:SS.mmm.HH:MM:SS.mmm
    pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3})\.(\d{2}:\d{2}:\d{2}\.\d{3})'
    # Replace with comma separator (correct SRT format)
    fixed_content = re.sub(pattern, r'\1,\2', srt_content)
    return fixed_content


def srt_to_sbv(srt_content: str) -> str:
    """
    Converts SRT format to SBV format.
    SRT:
    1
    00:00:00,000 --> 00:00:05,000
    Text line 1
    Text line 2

    SBV:
    0:00:00.000,0:00:05.000
    Text line 1
    Text line 2
    """
    sbv_blocks = []
    # Split by double newlines which typically separate SRT blocks
    blocks = srt_content.strip().split("\n\n")
    
    for block in blocks:
        lines = block.split("\n")
        if len(lines) < 3: 
            continue
            
        # SRT format:
        # Line 0: Index (1)
        # Line 1: Timestamp (00:00:00,000 --> 00:00:05,000)
        # Line 2+: Text
        
        # timestamp line
        timestamp_line = lines[1]
        text_lines = lines[2:]
        
        # Convert timestamp format
        # SRT: 00:00:00,000 --> 00:00:05,000
        # SBV: 0:00:00.000,0:00:05.000
        
        # Split by arrow to get start and end timestamps
        if " --> " in timestamp_line:
            start_time, end_time = timestamp_line.split(" --> ")
            # Replace milliseconds separator ',' with '.' in each part
            start_time = start_time.replace(",", ".")
            end_time = end_time.replace(",", ".")
            # Join with comma for SBV format
            sbv_timestamp = f"{start_time},{end_time}"
        else:
            # Fallback if format is unexpected
            sbv_timestamp = timestamp_line.replace(",", ".")
        
        # Join text lines
        text = "\n".join(text_lines)
        
        sbv_blocks.append(f"{sbv_timestamp}\n{text}")
        
    return "\n\n".join(sbv_blocks)


def transcribe_to_sbv(client: OpenAI, audio_path: Path, model: str, language: str, out_basename: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    sbv_path = OUTPUT_DIR / f"{out_basename}.sbv"

    with open(audio_path, "rb") as f:
        print(f"Transcribing {audio_path} (SRT) -> converting to {sbv_path} (SBV)")
        # Request SRT from OpenAI
        srt_transcript = client.audio.transcriptions.create(
            model=model,
            file=f,
            response_format="srt",
            language=language,
        )

    # Fix any malformed timestamps from Whisper
    srt_transcript = fix_whisper_timestamps(srt_transcript)
    
    # Convert to SBV
    sbv_transcript = srt_to_sbv(srt_transcript)

    with open(sbv_path, "w", encoding="utf-8") as f:
        f.write(sbv_transcript)
    return sbv_path


def generate_transcript(youtube_url: str, openai_api_key: str, model: str = "whisper-1", language: str = "fi", output_basename: str = "output") -> Path:
    """
    Main reusable function to download audio and generate an SBV transcript.
    """
    if not openai_api_key:
        raise ValueError("OpenAI API Key is missing.")

    client = OpenAI(api_key=openai_api_key)

    # 1. Download Audio
    print(f"Downloading audio from: {youtube_url}")
    audio_path = download_audio(youtube_url, output_basename)
    
    # 2. Transcribe
    print(f"Transcribing audio file: {audio_path}")
    sbv_path = transcribe_to_sbv(client, audio_path, model, language, output_basename)
    
    return sbv_path


def main():
    cfg = load_config()
    youtube_url = cfg["youtube_url"]
    out_basename = cfg.get("output_basename", "output")
    model = cfg.get("model", "whisper-1")
    language = cfg.get("language", "fi")
    api_key = cfg.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing (env or transcript_config.json).")

    try:
        sbv_path = generate_transcript(
            youtube_url=youtube_url, 
            openai_api_key=api_key, 
            model=model, 
            language=language, 
            output_basename=out_basename
        )
        print(f"\nDone. Upload this file to YouTube subtitles (With timing): {sbv_path}")
    except Exception as e:
        # Re-raise to be caught by the block below or just print here
        raise e


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print("Error running external command:", e, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)
