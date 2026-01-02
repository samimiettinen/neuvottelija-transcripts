---
description: Deploy Firebase Hosting
---

This workflow deploys the web UI to Firebase Hosting.

Prerequisites:
1. Ensure `public/firebase_config.json` is created and filled with credentials.
2. Login to Firebase: `firebase login`

Steps:

1. Deploy Hosting
// turbo
```bash
firebase deploy --only hosting
```

Or deploy everything (functions + hosting):

```bash
firebase deploy
```
