# Neuvottelija Transcripts

Työkalu YouTube-videoiden transkriptioiden luomiseen OpenAI Whisperin avulla.

## Ominaisuudet

- YouTube-videon äänen lataus
- Automaattinen transkriptio OpenAI Whisper API:lla
- Tuki SBV-formaatille (YouTube-tekstityksille)
- Graafinen käyttöliittymä (GUI)
- **UUSI:** Web-käyttöliittymä Firebase Auth -tunnistautumisella
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
   - Kopioi `transcript_config.example.json` → `transcript_config.json`
   ```bash
   copy transcript_config.example.json transcript_config.json
   ```
   - Muokkaa `transcript_config.json` ja lisää oma OpenAI API-avaimesi
   - **VAIHTOEHTO:** Aseta ympäristömuuttuja `OPENAI_API_KEY`
   
   **TÄRKEÄÄ:** `transcript_config.json` on `.gitignore`-tiedostossa, joten API-avaimesi pysyy turvassa!

4. Konfiguroi Firebase (Web UI:ta varten):
   - Kopioi `firebase_config.example.json` → `firebase_config.json`
   ```bash
   copy firebase_config.example.json firebase_config.json
   ```
   - Muokkaa `firebase_config.json` ja lisää Firebase-projektisi tiedot
   - Tämä vaaditaan vain, jos käytät Web-käyttöliittymää kirjautumiseen

## Käyttö

### Graafinen käyttöliittymä

Käynnistä Python GUI:
```bash
python -m src.transcript_gui
```

### Web-käyttöliittymä (Firebase Auth)

Tämä käyttöliittymä mahdollistaa kirjautumisen ja pilvifunktion kutsumisen:

```bash
python serve_ui.py
```
Tämä käynnistää paikallisen palvelimen osoitteessa `http://localhost:8000`.

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
