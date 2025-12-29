# Neuvottelija Transcripts

Automaattinen YouTube-videoidesi transkriptien generointi OpenAI Whisperillä.

## Asennus

1. Kloonaa repo:

```bash
git clone https://github.com/samimiettinen/neuvottelija-transcripts.git
cd neuvottelija-transcripts
```

2. Asenna riippuvuudet:

```bash
pip install -r requirements.txt
```

3. Kopioi `transcript_config.example.json` → `transcript_config.json` ja täytä:
- `openai_api_key`: oma OpenAI API-avaimesi
- `youtube_url`: video jonka haluat transkriptoida
- `output_basename`: haluttu tiedostonimi (esim. "neuvottelija1")

## Käyttö

```bash
python -m src.generate_transcript
```

Valmis SRT-tiedosto löytyy `output/`-kansiosta. Lataa se YouTubeen:
YouTube Studio → Content → valitse video → Subtitles → Add → Upload file → **With timing**

## Antigravity-käyttö (Windows)

1. Avaa projekti Antigravity-workspacena
2. Avaa terminal ja aja:

```bash
python -m src.generate_transcript
```

3. Tai pyydä agenttia ajamaan skripti

## Huomiot

- `transcript_config.json` on `.gitignore`ssa - älä committaa API-avaimia
- Audio- ja output-tiedostot eivät mene GitHubiin
- Whisper tukee suomea (`"language": "fi"`)
