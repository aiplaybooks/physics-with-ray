# Token rehberi (Physics with Ray)

Değerleri `.env` dosyasına yaz, sonra `python tools/set_secrets.py` ile GitHub Secrets'a yüklenir.

## Instagram (Instagram API with Instagram Login)
Hesap: Professional (Business/Creator). Meta App -> Instagram -> "API setup with Instagram login".
İzinler:
- `instagram_business_basic`
- `instagram_business_content_publish` (Reels yayını)
- `instagram_business_manage_comments` (ilk yorum)
- `instagram_business_manage_insights` (analytics)
Çıktılar: `IG_USER_ID`, `IG_TOKEN` (long-lived, 60 gün; yenilenmeli).

## Facebook Page
İzinler (Page access token):
- `pages_show_list`
- `pages_read_engagement`
- `pages_manage_posts` (Reels yükleme)
- `pages_manage_engagement` (ilk yorum)
- `read_insights` (analytics)
Çıktılar: `FB_PAGE_ID`, `FB_PAGE_TOKEN` (user token -> long-lived -> `me/accounts` ile süresiz page token), `FB_APP_ID`, `FB_APP_SECRET`.

## Diğer
- `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`: BotFather botu + chat id (bildirimler).
- `CLAUDE_CODE_OAUTH_TOKEN`: terminalde `claude setup-token` (otomatik ayar için).
