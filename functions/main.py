import os
import tempfile
import json
import re
from firebase_functions import https_fn, options
from firebase_admin import initialize_app, auth
import yt_dlp
from openai import OpenAI

initialize_app()

def fix_whisper_timestamps(srt_content: str) -> str:
    """
    Fixes malformed timestamps from Whisper where the range separator might be a period instead of comma.
    Converts: 00:00:00.000.00:00:08.000 -> 00:00:00.000,00:00:08.000
    """
    pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3})\.(\d{2}:\d{2}:\d{2}\.\d{3})'
    fixed_content = re.sub(pattern, r'\1,\2', srt_content)
    return fixed_content

def srt_to_sbv(srt_content: str) -> str:
    """
    Converts SRT format to SBV format.
    """
    sbv_blocks = []
    blocks = srt_content.strip().split("\n\n")
    
    for block in blocks:
        lines = block.split("\n")
        if len(lines) < 3: 
            continue
            
        timestamp_line = lines[1]
        text_lines = lines[2:]
        
        if " --> " in timestamp_line:
            start_time, end_time = timestamp_line.split(" --> ")
            start_time = start_time.replace(",", ".")
            end_time = end_time.replace(",", ".")
            sbv_timestamp = f"{start_time},{end_time}"
        else:
            sbv_timestamp = timestamp_line.replace(",", ".")
        
        text = "\n".join(text_lines)
        sbv_blocks.append(f"{sbv_timestamp}\n{text}")
        
    return "\n\n".join(sbv_blocks)

@https_fn.on_request(
    timeout_sec=540,  # 9 minutes
    memory=options.MemoryOption.GB_2,
    region="europe-west1", # Or use default us-central1 if preferred, but user mentioned neuvottelija might be EU based
    cors=options.CorsOptions(cors_origins="*", cors_methods=["post"])
)
def runTranscript(req: https_fn.Request) -> https_fn.Response:
    """
    HTTPS Cloud Function that:
    1. Verifies Firebase Auth ID Token from Authorization header
    2. Downloads YouTube audio
    3. Transcribes with OpenAI Whisper
    4. Returns SBV transcript
    """
    
    # 1. CORS Preflight is handled by `cors` option in decorator for 2nd gen functions, 
    # but let's be safe and check method.
    if req.method != "POST":
        return https_fn.Response("Method not allowed", status=405)

    # 2. Verify Auth Token
    auth_header = req.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return https_fn.Response("Unauthorized: Missing Bearer token", status=401)
    
    id_token = auth_header.split("Bearer ")[1]
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        print(f"Authenticated user: {uid}")
    except Exception as e:
        print(f"Auth error: {e}")
        return https_fn.Response(f"Unauthorized: Invalid token. {str(e)}", status=401)

    # 3. Parse Request
    try:
        data = req.get_json()
        youtube_url = data.get("youtube_url")
        if not youtube_url:
            return https_fn.Response("Missing 'youtube_url' in body", status=400)
    except Exception as e:
        return https_fn.Response(f"Invalid JSON: {str(e)}", status=400)

    # 4. Check API Key
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        # Try to get from request for flexibility (though less secure if not careful)
        # But for this assignment, let's assume env var or fail.
        return https_fn.Response("Server config error: OPENAI_API_KEY missing", status=500)

    # 5. Download & Transcribe
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = os.path.join(temp_dir, "%(title)s.%(ext)s")
            
            # Download specific audio format supported by Whisper (m4a is usually safe and small)
            ydl_opts = {
                'format': 'm4a/bestaudio/best',
                'outtmpl': temp_path,
                'quiet': True,
                'no_warnings': True,
            }
            
            print(f"Downloading {youtube_url}...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                downloaded_file = ydl.prepare_filename(info)
            
            print(f"Downloaded to {downloaded_file}")
            
            # Transcribe
            client = OpenAI(api_key=openai_api_key)
            
            with open(downloaded_file, "rb") as audio_file:
                print("Calling Whisper API...")
                srt_transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="srt",
                    language="fi" # Default to FI as per original code context
                )
            
            # Process Transcript
            fixed_srt = fix_whisper_timestamps(srt_transcript)
            sbv_transcript = srt_to_sbv(fixed_srt)
            
            return https_fn.Response(json.dumps({
                "message": "Transcription successful",
                "sbv_content": sbv_transcript,
                "video_title": info.get('title', 'video')
            }), status=200, headers={"Content-Type": "application/json"})
            
    except Exception as e:
        print(f"Error during processing: {e}")
        return https_fn.Response(f"Processing error: {str(e)}", status=500)
