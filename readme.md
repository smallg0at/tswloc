# Train Sim World DLC Chinese Translation

[简体中文](./readme_zh.md)

This repository is the working source for the TSW Simplified Chinese localization project by 联络线汉化组.

The translations within this repository are made by @smallg0at, @ibox233, Saber_Pike and archetype.

Important: The localization sources of some packs are not seen here and you should not assume the csvs for them exist.

## Coverage in This Repo

The repository includes localization/fix content for multiple third-party DLC packs. The specific list can be seen here:

https://www.trainsimcommunity.com/mods/c3-train-sim-world/c19-patches/i7144-dlc-145br145-third-party-dlc-simplified-chinese-localisation-and-fixes-145

## Installation

Steam: place pak files into `<Documents>\My Games\TrainSimWorld6\Saved\UserContent`.

Epic: place pak files into `<Documents>\My Games\TrainSimWorld6EGS\Saved\UserContent`.

If `UserContent` does not exist, create it manually and make sure mods are enabled in game settings.

## Full Localization Tutorial

### 0. Adapting to Another Language

This repo is currently wired for zh/zh-CN paths.

**Fork this repo first.**

If you fork for another target language, replace language codes consistently across the project IN EXACT ORDER:

- zh-CN -> your target locale code
- zh -> your target folder code

Clean up everything in original, dist, riviera_patch folders.
Remove ALL csvs in the project root dir.

### 1. Prerequisites

- Python 3
  - with Google Cloud API & GenAI packages installed
  - (if you want to use their services instead of other translators)
- repak in PATH
- Utils/UnrealLocres.exe (already included in this repo)
- Optional API credentials for auto-translation:
  - GOOGLE_APPLICATION_CREDENTIALS for translate.py
  - GEMINI_API_KEY in environment variables for translate-next.py
  - (if you want to use their services instead of other translators)

> [!WARNING]
> DO NOT EVER UPLOAD YOUR KEY TO A GITHUB REPO. If you plan to save it around here add to `.gitignore` first.

### 2. Folder Roles in This Repo

- original/: source DLC localization files to export from
- root CSV files: editable translation tables (*.locres.csv and *_translated.csv)
- dist/: final localized locres tree used for packing
- riviera_patch/: separate patch tree for Riviera fix package
- dist_godmode/: final localized locres tree for the separate Foob_GodMode pack
- csv/csv_godmode/: translation table for the Foob_GodMode pack (Foob_GodMode_translated.csv)

### 3. repak Basics (Required)

repak is used in two places:

- unpacking DLC paks to retrieve localization assets
- packing this repo output back into mod paks

Quick check:

repak --help

If the command is not found, install repak first and make sure it is available in PATH.

### 4. Proper Extract from DLC pak (locres only)

Do not unpack the entire DLC pak. First list paths and filter for localization files, then unpack only the required files.

#### Automatic

Find getlocresscript.ps1, set `Set-Location` to the DLC folder, edit the params on the top and run it.

You may have to tweak script running policy.

#### Manual

1. List localization paths in the source pak:

    `repak list "C:\path\to\DLC.pak" | sls "Localization"`

2. Identify only the correct locres files for your source language:

- `TS2Prototype/Plugins/DLC/<PackName>/Content/Localization/<PackName>/en/<PackName>.locres`
- or `TS2Prototype/Plugins/DLC/<PackName>/Content/Localization/<PackName>/en-GB/<PackName>.locres`

3. Unpack only those locres paths:

    `repak unpack "C:\path\to\DLC.pak" --include "TS2Prototype/Plugins/DLC/<PackName>/Content/Localization/<PackName>/en/<PackName>.locres" --include "<filepath2>" --output "./original"`

    If a pack uses en-GB instead of en, replace the include path accordingly.

4. Verify final source layout:

    `original/TS2Prototype/Plugins/DLC/<PackName>/Content/Localization/<PackName>/en/<PackName>.locres`

    or `original/TS2Prototype/Plugins/DLC/<PackName>/Content/Localization/<PackName>/en-GB/<PackName>.locres`

### 5. Prepare Source Files

Put DLC localization files under original/TS2Prototype/Plugins/DLC/<PackName>/Content/Localization/<PackName>/en or en-GB.
Copy them to dist folder, then change all folder hierarchy named `en` or `en-GB` to your destination.
Example: dist/TS2Prototype/Plugins/DLC/<PackName>/Content/Localization/<PackName>/<langcode>.

Example source file shape:

```
original/TS2Prototype/Plugins/DLC/AABS_Class805/Content/Localization/AABS_Class805/en/AABS_Class805.locres
dist/TS2Prototype/Plugins/DLC/AABS_Class805/Content/Localization/AABS_Class805/zh/AABS_Class805.locres
```

### 6. Extract locres into CSV

Run:

`python command_helper.py extract`

What it does:

- scans original/TS2Prototype/Plugins/DLC
- finds en-GB or en locres
- exports each pack into a root-level <PackName>.locres.csv

### 7. Translate CSV

Pick one helper based on your target quality/speed.

translate.py (Google Cloud Translate v2):

- uses GOOGLE_APPLICATION_CREDENTIALS
- Horrible quality, but cheap.
- applies glossary.csv term replacement after translation
- outputs <PackName>_translated.csv

translate-next.py (Gemini API):

- uses GEMINI_API_KEY
- enforces stricter translation rules for rail terminology and formatting
- returns structured JSON output and maps back into CSV
- Preferred

translate-next-tbt.py (Gemini API, TBT rows only):

- same engine/rules as translate-next.py, but only translates rows whose `target` column is exactly `TBT`, leaving every other row untouched
- overwrites the input file in place (set `FILE` to a `_translated.csv` name, not a `.locres.csv`)
- use this after `merge`/`godmode-extract` add new `TBT` placeholder rows to an already-translated csv, instead of re-translating the whole file

Important:

- Set TARGET_LANG and FILE inside the chosen helper script before running.
- Keep glossary.csv updated before bulk translation.

### 8. Manual QA Pass

Open the generated *_translated.csv and review at least:

- station names
- service names and route patterns
- placeholders like {0}, {1}, {TrainName} (must remain intact)
- abbreviations that should stay as rail terms

Optional utility:

- merge.py can merge selected columns from one CSV into another when doing partial replacement.
- reprocess.py fills any row still marked `TBT` by copying the translation from another row in the same file that shares the exact same `source` text and is already translated. Run it before translate-next-tbt.py to dedupe repeated strings for free: `python reprocess.py ./csv/<PackName>_translated.csv`.

### 9. Apply Translations Back to locres

Run:

python command_helper.py apply

What it does:

- imports each root-level *_translated.csv
- writes into dist/TS2Prototype/Plugins/DLC/<PackName>/Content/Localization/<PackName>/zh/<PackName>.locres

### 10. Pack mod files

Main package:

python command_helper.py pack

- builds ZHLoc.pak from dist/
- tries to auto-copy ZHLoc.pak to your Train Sim World 6 UserContent folder in Documents

Riviera patch package:

python command_helper.py pack-riviera

- builds ZHLoc-riviera-fix.pak from riviera_patch/

### 11. Install and Test In-Game

Steam:

<Documents>\My Games\TrainSimWorld6\Saved\UserContent

Epic:

<Documents>\My Games\TrainSimWorld6EGS\Saved\UserContent

If UserContent is missing, create it manually.
Enable mods in game settings (Advanced -> Enable Mods).

### 12. Updating a Pack After a DLC Patch

`dist/` zh locres files are binaries with a fixed set of key slots. `apply` can only overwrite text for keys that already exist in that binary — it cannot add new key slots, so a patch that introduces new strings needs an extra `override` pass to rebuild the structure before `apply` will pick those new keys up.

1. Grab the updated locres out of the new DLC pak with `getlocresscript.ps1`: edit `$pakFile` (the new pak's filename) and the `Set-Location` path (your local DLC install folder) at the top of the script, then run it. It unpacks only the en/en-GB/zh locres paths into `original/`, overwriting the old `original/.../en[-GB]/<PackName>.locres`.
   - Do not touch `dist/.../zh/<PackName>.locres` yet — `merge` needs its current (pre-update) content.
2. Run `python command_helper.py merge`. It loops over every pack in `original/`; for each one with an existing `./csv/<PackName>_translated.csv` it asks for confirmation. Answer `y` only for the pack(s) you actually updated (unaffected packs' csvs are already accurate and don't need re-merging — answer `n`/skip for those). For the updated pack, it re-exports the new en locres and the still-old `dist/` zh locres, matches rows by `key`, carries over the previous zh text for keys that already existed, and marks brand-new keys `TBT` (printed to the console).

    > [!WARNING]
    > Matching is by key only, not by text diff. If the patch edits the English text under a key that already existed, `merge` still carries over the *old* translation under that key without flagging it. Spot check if you suspect in-place text edits.
3. Run `python command_helper.py override`. This force-copies the (now updated) en/en-GB locres over the zh slot in `dist/` for every pack, rebuilding each one's key structure to match current `original/` content. This is safe now because step 2 already pulled every translation you care about into the csvs — `override` only touches the `dist/` binaries, never the csvs.
4. Fill in the new `TBT` rows in `./csv/<PackName>_translated.csv`:
   - `python reprocess.py ./csv/<PackName>_translated.csv` first — fills any `TBT` row whose `source` text exactly matches another row that's already translated, for free.
   - Then set `FILE = "<PackName>_translated.csv"` in translate-next-tbt.py and run it — it AI-translates only the rows still marked `TBT` and overwrites the same file in place, leaving everything else untouched.
   - Manually QA the newly translated rows (see steps 7-8).
5. `python command_helper.py apply` then `python command_helper.py pack` (or the `godmode-*` equivalents for Foob_GodMode, using `godmode-extract` in place of `merge` in step 2).

## command_helper.py Command Reference

Run `python command_helper.py` with no arguments to print this list.

| Command | What it does |
| --- | --- |
| `extract` | Exports en/en-GB locres from `original/` into `./csv/<PackName>.locres.csv` for every pack (skips `Foob_GodMode`). |
| `apply` | Imports every `./csv/*_translated.csv` back into `dist/.../zh/<PackName>.locres`. |
| `merge` | For a pack that already has a `./csv/<PackName>_translated.csv`, re-exports both the en and the current zh locres and merges them, preferring the existing zh text where the en source still matches. Useful after a DLC update added new strings to re-sync without losing existing translations. Asks for confirmation before overwriting, and skips packs with no existing translated csv. |
| `override` | Force-copies the en/en-GB locres over the zh slot in `dist/` for every pack, unconditionally and without confirmation. Rebuilds each pack's key structure to match current `original/` content — required after a DLC patch adds new strings, and only safe to run after `merge` has harvested existing translations into the csvs (see section 12). |
| `pack` | Runs `repak` on `dist/` to build `ZHLoc.pak`, then copies it into the TSW6 UserContent folder. |
| `pack-riviera` | Runs `repak` on `riviera_patch/` to build `ZHLoc-riviera-fix.pak`. |
| `godmode-extract` | Same idea as `merge`, scoped to the `Foob_GodMode` pack: merges `original/` (en) and `dist_godmode/` (zh) into `./csv/csv_godmode/Foob_GodMode_translated.csv`. |
| `godmode-apply` | Imports `./csv/csv_godmode/Foob_GodMode_translated.csv` into `dist_godmode/.../zh/Foob_GodMode.locres`. |
| `godmode-pack` | Runs `repak` on `dist_godmode/` to build `ZHLoc-GodMode.pak`, then copies it into the TSW6 UserContent folder. |

## Notes

- Manuals/Liberec-Stara_Paka_Manual contains manual translation assets (including zh-CN outputs).

## License

This project uses a modified WTFPL variant.

[DO WHAT THE FUCK YOU WANT TO IF ITS FREE PUBLIC LICENSE](./license)