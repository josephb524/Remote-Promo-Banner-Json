#!/usr/bin/env python3
"""Checks apps.json before it is pushed. Run: python3 validate.py

The apps list is live data: pushing it changes what every installed hymnal
shows within minutes, with no app update and no review. There is no build to
catch a mistake, so the rules live here. See README.md for what they mean.
"""

import json
import sys

HYMNAL_SLUGS = {
    "adventist-hymnal",      # Official Adventist Hymnal (English)
    "himnario-adventista",   # Himnario Adventista (Spanish)
    "chantsdesperance",      # Chants d'Espérance (Haitian French)
    "harpacrista",           # Harpa Cristã (Brazilian Portuguese)
}
ADVENTIST_SLUGS = {"adventist-hymnal", "himnario-adventista"}
# Which interface language each hymnal reads (AppStoreConfig/HymnalConfig languageKey).
HYMNAL_LANGUAGE = {
    "adventist-hymnal": "en",
    "himnario-adventista": "es",
    "chantsdesperance": "fr",
    "harpacrista": "pt",
}
REQUIRED = ["id", "isActive", "icon", "store", "clickURL", "name", "pitch",
            "audience", "languages"]
LANGS = ["en", "es", "fr", "pt"]

errors: list[str] = []
warnings: list[str] = []


def hymnals_showing(app: dict) -> set:
    """The hymnals this entry can appear in, ignoring the country filter."""
    only_in = app.get("onlyIn") or []
    reach = {s for s in only_in if s in HYMNAL_SLUGS} if only_in else set(HYMNAL_SLUGS)
    return reach - {app["id"]}


def main() -> int:
    try:
        data = json.load(open("apps.json", encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"apps.json does not parse: {exc}")
        return 1

    seen = set()
    for app in data.get("apps", []):
        aid = app.get("id", "<no id>")

        for key in REQUIRED:
            if key not in app:
                errors.append(f"{aid}: missing required key {key!r}")
        if aid in seen:
            errors.append(f"{aid}: duplicate id")
        seen.add(aid)

        for field in ("name", "pitch"):
            for lang in LANGS:
                if not app.get(field, {}).get(lang):
                    errors.append(f"{aid}: {field} has no {lang!r} text")

        for slug in app.get("onlyIn") or []:
            if slug not in HYMNAL_SLUGS:
                errors.append(f"{aid}: onlyIn names an unknown hymnal {slug!r}")

        audience = app.get("audience")
        if audience not in ("adventist", "general"):
            errors.append(f"{aid}: audience must be 'adventist' or 'general'")
        elif audience == "adventist":
            # Rule 1. An Adventist-only app must never reach a hymnal of
            # another denomination. Harpa Cristã is Assemblies of God and
            # Chants d'Espérance is a Haitian French hymnal.
            stray = hymnals_showing(app) - ADVENTIST_SLUGS
            if stray:
                errors.append(
                    f"{aid}: audience 'adventist' but it would show in "
                    f"{sorted(stray)}. Add onlyIn: {sorted(ADVENTIST_SLUGS)}")

        # Rule 2. Do not pitch an app in a language its interface does not
        # speak without saying so in that pitch.
        languages = app.get("languages") or []
        if not languages:
            errors.append(f"{aid}: languages is empty")
        for slug in sorted(hymnals_showing(app)):
            lang = HYMNAL_LANGUAGE[slug]
            if lang in languages:
                continue
            pitch = app.get("pitch", {}).get(lang, "")
            spoken = [n for lg, n in (("en", "anglais|inglês|English|inglés"),
                                      ("es", "espagnol|espanhol|Spanish|español"),
                                      ("fr", "français|francês|French|francés"),
                                      ("pt", "portugais|português|Portuguese|portugués"))
                      if lg in languages]
            if not any(any(word in pitch for word in group.split("|"))
                       for group in spoken):
                errors.append(
                    f"{aid}: shows in {slug} ({lang}) but the app is "
                    f"{'/'.join(languages)} only, and the {lang} pitch does "
                    f"not say so")

    for line in warnings:
        print(f"warning: {line}")
    for line in errors:
        print(f"error:   {line}")

    if errors:
        print(f"\n{len(errors)} error(s). Do not push.")
        return 1
    print(f"apps.json is valid ({len(seen)} apps, {len(warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
