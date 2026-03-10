# Browser Cookies

## Goal

Some publishers allow access only after a user has completed login, institutional proxy authentication, or a browser challenge. Paper-Reach can reuse that user-authorized session if you export the necessary cookies or headers locally.

This is not a bypass mechanism. It is a way to reuse your own already-authorized browser session.

## Supported Inputs

Paper-Reach accepts:

- a cookie JSON file
- a Mozilla/Netscape cookiejar export
- a JSON header file

Examples:

- [examples/auth/cookies.example.json](/home/nas/dailing/paper_reach/examples/auth/cookies.example.json)
- [examples/auth/headers.example.json](/home/nas/dailing/paper_reach/examples/auth/headers.example.json)

## Typical Workflow

1. Open the publisher page in your browser.
2. Complete login or institutional authentication if needed.
3. If the site uses a challenge page, finish it in the browser first.
4. Export the relevant cookies.
5. Pass the cookie file to `paper-reach fetch-fulltext`.

## JSON Cookie Format

Minimal JSON format:

```json
{
  "sessionid": "your-cookie-value",
  "cf_clearance": "your-challenge-cookie-if-present"
}
```

## JSON Header Format

Some sites also respond better when a session is accompanied by stable headers:

```json
{
  "Referer": "https://www.cell.com/",
  "Accept-Language": "en-US,en;q=0.9"
}
```

## Command Example

```bash
paper-reach fetch-fulltext \
  --input query.json \
  --output review.json \
  --download-dir ./downloads \
  --cookie-file ./cookies.json \
  --header-file ./headers.json
```

## What To Expect

- if the session is still valid, Paper-Reach may download the PDF automatically
- if the session expired, the result will remain `login_required`, `challenge`, or `restricted`
- if the page has no accessible PDF, the result will remain `not_found`

## Limitations

- exported sessions may expire quickly
- different publishers require different cookies
- some sites block automated requests even after normal browser access

