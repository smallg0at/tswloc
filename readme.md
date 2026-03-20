# Train Sim World DLC Chinese Translation

[简体中文](./readme_zh.md)

This repository is the working source for my TSW Simplified Chinese localization project.

## Current Repository Status

- Root currently contains 25 `*.locres.csv` source tables and 25 `*_translated.csv` tables.
- Main build output is `ZHLoc.pak`.
- Extra patch build output is `ZHLoc-riviera-fix.pak` (Riviera display/title fix).
- `ZHLoc-145.pak` and `!145_PartialTranslate.pak` are packaged artifacts only.
- Important: BR145 translation content is not my translation source work in this repo, so there are no BR145 translation CSV files in the root.

## Coverage in This Repo

The repository includes localization/fix content for multiple third-party DLC packs (for example AWC 805, Birmingham-Crewe related content, Class 170 related content, Southern 171/377-3, Liberec-Stara Paka, and others visible in the CSV list).

This matches the public mod direction and ongoing updates on Train Sim Community:
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

Copy getlocresscript.ps1 to the DLC folder, edit the params on the top and run it.

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


## Notes

- Manuals/Liberec-Stara_Paka_Manual contains manual translation assets (including zh-CN outputs).
- BR145 translation source CSV is intentionally not included in root because BR145 localization content is from third-party contributors; related files here are package artifacts only.

## License

This project uses a modified WTFPL variant.

[DO WHAT THE FUCK YOU WANT TO IF ITS FREE PUBLIC LICENSE](./license)