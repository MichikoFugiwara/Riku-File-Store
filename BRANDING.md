# Riku File Store

This project has been rebranded as **Riku File Store**.

## Branding changes
- Bot session and default MongoDB database name use `riku` / `riku_file_store`.
- Start, force-subscription, about, reply, and short-link messages use Riku branding.
- Old third-party owner, channel, and promotional links were removed from user-facing defaults.
- Start and force-subscription image URLs are blank by default; add your own image URL in `config.py` or through the bot settings.

## Required configuration
Copy `.env.example` values into your hosting provider's Environment Variables. Replace every example value with your own credentials and IDs. Never publish your real bot token, API hash, or MongoDB password.

`DB_CHANNEL` must be a private Telegram channel ID where the bot is an administrator with permission to post and delete messages. `OWNER_ID` must be your numeric Telegram user ID. Add the bot to that database channel before starting it.

## Notes
- Existing feature code and the upstream license file are retained.
- This is a branding/configuration pass, not a guarantee that every runtime integration has been tested against your live Telegram and MongoDB accounts.
