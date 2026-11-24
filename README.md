# Madni Jamia Masjid screen

Needs Node 18 or newer. No other dependencies.

    ADMIN_PASSWORD=choose-a-password node server.js

- Screen: http://localhost:3000
- Admin:  http://localhost:3000/admin

Optional: set ANTHROPIC_API_KEY to enable "Read with AI" for prayer calendar images (more accurate than OCR).
Settings and uploads are saved in the data/ folder – back it up.

## Running on a TV
Chromium kiosk: `chromium-browser --kiosk --noerrdialogs --disable-infobars http://SERVER:3000`
The screen refreshes its settings every 30 seconds.

## Deploying
Any Node host works (VPS, Raspberry Pi, Render, Railway). Put it behind HTTPS and keep ADMIN_PASSWORD secret.
Fonts and OCR load from Google Fonts / jsDelivr; the screen falls back to system fonts if offline.
