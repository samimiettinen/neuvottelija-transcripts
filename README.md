# Neuvottelija Transcripts

Työkalu YouTube-videoiden transkriptioiden luomiseen OpenAI Whisperin avulla.

## Ominaisuudet

- YouTube-videon äänen lataus
- Automaattinen transkriptio OpenAI Whisper API:lla
- Tuki SBV-formaatille (YouTube-tekstityksille)
- Graafinen käyttöliittymä (GUI)
- Korjaa automaattisesti Whisperin aikaleimaongelmat

## Asennus

1. Kloonaa repository:
```bash
git clone https://github.com/samimiettinen/neuvottelija-transcripts.git
cd neuvottelija-transcripts
```

2. Asenna riippuvuudet:
```bash
pip install openai yt-dlp
```

3. Konfiguroi API-avain:
   - Kopioi `transcript_config.json` ja lisää oma OpenAI API-avaimesi
   - TAI aseta ympäristömuuttuja: `OPENAI_API_KEY`

## Käyttö

### Graafinen käyttöliittymä

Käynnistä GUI:
```bash
python -m src.transcript_gui
```

### Komentorivi

Suorita skripti:
```bash
python -m src.generate_transcript
```

## Konfiguraatio

Muokkaa `transcript_config.json`:
```json
{
    "youtube_url": "https://youtu.be/VIDEO_ID",
    "output_basename": "transcript_output",
    "model": "whisper-1",
    "language": "fi",
    "openai_api_key": "YOUR_OPENAI_API_KEY_HERE"
}
```

## Turvallisuus

**TÄRKEÄÄ:** Älä koskaan committaa oikeaa API-avainta GitHubiin!
- API-avaimet on lisätty `.gitignore`-tiedostoon
- Käytä ympäristömuuttujia tai paikallista config-tiedostoa

## Tekijä

Sami Miettinen
