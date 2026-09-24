# Remote promo content

Live data for Jose Pimentel's hymnal apps. **Pushing to `main` changes what
every installed app shows within minutes** — no app update, no App Store
review, no way to take it back except another push. There is no build step to
catch a mistake, so read the rules below before editing.

Run `python3 validate.py` before every push. It fails on the mistakes that
have actually happened here.

## Files

| File | Used by |
|---|---|
| `apps.json` | The "More apps" list in all four hymnals |
| `PromoBannerEN.json` / `PromoBannerSpanish.json` | Banners in the English / Spanish hymnals |
| `PromoBannerFR.json` / `PromoBannerPT.json` | Banners in the French / Portuguese hymnals |
| `PromoBannerCairn.json` / `PromoBannerHearken.json` / `PromoBannerInterlinear.json` | Banners in those apps |
| `*.png` | Icons, fetched directly by the apps and proxied by the promo-tracker Worker |

## The four hymnals

The slug is each app's `selfAppSlug` (`AppStoreConfig.swift`, or
`HymnalConfig.swift` in the French and Portuguese apps). An app never lists
itself.

| Slug | App | Language | Denomination |
|---|---|---|---|
| `adventist-hymnal` | Official Adventist Hymnal | `en` | Seventh-day Adventist |
| `himnario-adventista` | Himnario Adventista | `es` | Seventh-day Adventist |
| `chantsdesperance` | Chants d'Espérance | `fr` | Haitian, interdenominational |
| `harpacrista` | Harpa Cristã | `pt` | Assemblies of God (Brazil) |

**The last two are not Adventist apps.** That is the point of rule 1.

## `apps.json` entry

```json
{
  "id": "cairn",
  "icon": "https://raw.githubusercontent.com/josephb524/Remote-Promo-Banner-Json/main/Cairn.png",
  "store": "https://apps.apple.com/app/apple-store/id6805641022?pt=121666584&ct=apps-list&mt=8",
  "clickURL": "https://promo-tracker.bible-chat-worker.workers.dev/hit/cairn?from=apps-list",
  "name":  { "en": "...", "es": "...", "fr": "...", "pt": "..." },
  "pitch": { "en": "...", "es": "...", "fr": "...", "pt": "..." },
  "countries": [],
  "isActive": true,
  "audience": "general",
  "languages": ["en", "es"]
}
```

- `isActive` — `false` hides the entry everywhere.
- `countries` — ISO codes the app is sold in; empty means everywhere. Filtered
  against the device region, so an entry never advertises an app the user
  cannot download.
- `onlyIn` — the hymnal slugs allowed to show this entry. Absent or empty
  means **all four**, which is what caused the bug rule 1 now prevents.
- `audience`, `languages` — read only by `validate.py`; the apps ignore
  unknown keys. Keep them truthful, because the rules are enforced from them.
- `store` keeps `ct=apps-list` so App Store Connect separates these installs
  from banner installs. `clickURL` is the tracker beacon; icons come from raw
  GitHub, never the Worker's `/img/`, so opening the list costs no impression.

## Rule 1 — an Adventist app goes only in the Adventist hymnals

An entry with `"audience": "adventist"` must carry
`"onlyIn": ["adventist-hymnal", "himnario-adventista"]`.

On 2026-09-24 the Maranatha (Adventist dating) entry had a country filter but
no `onlyIn`, so it was being advertised inside an Assemblies of God hymnal and
a Haitian French one. `validate.py` now fails on this.

## Rule 2 — do not pitch an app in a language it does not speak

If an entry can appear in a hymnal whose language is missing from its
`languages`, that language's `pitch` must say what the app is actually in.

Cairn, Hearken and Interlinear Bible are English and Spanish only, yet they
appear in the French and Portuguese hymnals, so their `fr` and `pt` pitches end
with `App en anglais et en espagnol.` / `App em inglês e espanhol.` Otherwise a
Haitian reader taps a French sales line and lands in an English app. The
La Fe de Jesús entry has always done this correctly.

## Editing

1. Edit the JSON. Keep two-space indentation and literal accents; the files
   round-trip through `json.dumps(data, indent=2, ensure_ascii=False) + "\n"`.
2. `python3 validate.py`
3. Commit and push. Verify in a running app by backgrounding and reopening it —
   every list refetches on foreground and caches the last good copy for offline.
