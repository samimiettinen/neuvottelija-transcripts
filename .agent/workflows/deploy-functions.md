---
description: Deploy Firebase Cloud Functions
---

This workflow deploys the Python Cloud Functions to Firebase.

Prerequisites:
1. Ensure you have installed Node.js and Firebase CLI: `npm install -g firebase-tools`
2. Ensure you have Python 3.11 installed.
3. Login to Firebase: `firebase login`
4. Set the OpenAI API Key in Cloud Functions config:
   `firebase functions:secrets:set OPENAI_API_KEY` (if using secrets)
   OR for simple env var:
   `firebase functions:config:set run_transcript.openai_api_key="YOUR_KEY"` 
   (Note: The code currently looks for `OPENAI_API_KEY` os.environ, which can be set via `firebase functions:config:set` but manifests as build envs or runtime envs differently in Gen 2. For Gen 2, prefer: `firebase functions:secrets:set OPENAI_API_KEY` and update code to use secrets, or use .env file for deploy)

For 2nd Gen functions, it's easiest to create a `.env` file in `functions/` directory before deploying:

```bash
# functions/.env
OPENAI_API_KEY=your-key-here
```

Steps to deploy:

1. Create the .env file with your API Key
// turbo
2. Deploy the functions
```bash
firebase deploy --only functions
```
