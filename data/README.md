# Public data sources

Downloaded source material belongs in `data/raw/` and normalized output belongs
in `data/processed/`; both directories are intentionally ignored by Git. Run
`make data` from the repository root. The command processes sources it can use
and prints actionable instructions for sources that need credentials, consent,
or a manual download.

The normalized files use these columns:

`id,text,label,channel,source,license,collected_at`

`label` is `scam` or `legit`; `collected_at` is an ISO 8601 UTC timestamp for
when the local copy was created.

## UCI SMS Spam Collection

- Source: <https://archive.ics.uci.edu/dataset/228/sms+spam+collection>
- Download: <https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip>
- DOI: <https://doi.org/10.24432/C5CC84>
- License: Creative Commons Attribution 4.0 (CC BY 4.0).
- Registration: none.
- Usage: downloaded automatically. The ZIP integrity, expected member, row
  count (5,574), label set, and non-empty messages are verified before output.

## SpearPhishMX email corpus

- Source: <https://data.mendeley.com/datasets/h4bxjk84jb/1>
- DOI: <https://doi.org/10.17632/h4bxjk84jb.1>
- License: Creative Commons Attribution 4.0 (CC BY 4.0).
- Registration: the public record is open; Mendeley's interactive download may
  request sign-in depending on the session. No stable, documented direct file
  URL is used by this repository.
- Usage: this defensive-research corpus contains both spear-phishing and
  legitimate Spanish email (`etiqueta=1` and `etiqueta=0`). Download
  `SpearPhishMX_dataset_publico.csv` manually, place it at
  `data/raw/email/SpearPhishMX_dataset_publico.csv`, and rerun `make data`.
  Only the sanitized body is processed; never reactivate its defanged URLs.

This single openly licensed corpus supplies both the requested public phishing
email examples and legitimate email examples. It is kept manual so a changed
Mendeley session URL cannot silently fetch the wrong artifact.

## URLhaus

- Source/API: <https://urlhaus.abuse.ch/api/>
- Terms: <https://abuse.ch/terms/>
- License/usage: abuse.ch Community API Terms and fair-use conditions; commercial
  users may require an enhanced API subscription.
- Registration: required. Obtain a free Auth-Key through the abuse.ch
  Authentication Portal and set `URLHAUS_AUTH_KEY` locally.
- Usage: downloads the official `recent.csv` v2 export. URLhaus tracks malware
  delivery URLs, not phishing URLs; keep that distinction when analyzing it.

## OpenPhish Community Feed

- Source: <https://openphish.com/phishing_feeds.html>
- Feed: <https://raw.githubusercontent.com/openphish/public_feed/main/feed.txt>
- Terms: <https://openphish.com/terms.html>
- License/usage: proprietary Terms of Use, **non-commercial research only**.
- Registration: none for the community feed.
- Usage: because the product may eventually be commercial, the downloader does
  not fetch this feed until the user has reviewed the current terms and sets
  `SCAMGUARD_ACCEPT_OPENPHISH_TERMS=1`. Do not ship or redistribute this data.

## PhishTank (optional)

- Developer documentation: <https://www.phishtank.com/developer_info.php>
- License/usage: PhishTank site and API terms; verified phishing URLs are for
  defensive research and must not be treated as safe browsing targets.
- Registration: optional for heavily rate-limited anonymous downloads, but this
  project requires an application key to avoid unreliable anonymous access.
- Usage: set `PHISHTANK_API_KEY` locally. The key is used only at request time
  and must never be committed.

## Safety and scope

Threat feeds contain live or formerly live malicious URLs. They are for
detection research only: do not click, crawl, resolve, redistribute, or use them
as a production blocklist without a separate legal, safety, and quality review.
Public labels can be stale or wrong. None of these sources is user telemetry.

