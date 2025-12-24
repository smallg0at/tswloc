# Train Sim World DLC Chinese Translation

[简体中文](./readme_zh.md)

Because the official localization team cannot handle up to 17 third‑party DLCs on the roadmap and only provides English and German, I did the translations by myself with the help of Google Translate. This repository contains all the original translation source files.

Although this code is used for Chinese translation, it can also be used by other languages as well!

Currently localized DLCs:

- ✅ Birmingham Cross‑City Line — Class 170 (Rivet Games)
- ✅ West Coast Main Line: Birmingham–Crewe (AABS)

## Installation

Steam: place the .pak file into `<Documents>\My Games\TrainSimWorld6\Saved\UserContent`.
Epic: place the .pak file into `<Documents>\My Games\TrainSimWorld6EGS\Saved\UserContent`.

## Development

- Prerequisites
    - Install unpak and Python (with required deps).
    - Google Cloud account: authenticate (gcloud auth application-default login) or set GOOGLE_APPLICATION_CREDENTIALS to a service-account JSON.
    - **\[IMPORTANT\]** Prepare/adjust glossary.csv before automated translation. I advice to use the current list but change all keys to your languages separately, because you will suffer in correction later if you don't do that.

- Unpack with unpak
    1. Locate the DLC .pak file (Steam/Epic install or exported copy). Ctrl+Shift+C to get its path.
    2. Extract language files to dist folder (example commands — check unpak --help for exact flags on your build):
         - Windows example:
             - unpak extract "C:\path\to\DLC.pak" -o ".\dist\"
    3. Verify the extracted language files (`.locres`) are inside, path is usually like `dist\TS2Prototype\Plugins\DLC\AABS_Class350_BTP\Content\Localization\AABS_Class350_BTP\en-GB\AABS_Class350_BTP.locres`.
    4. Change the `en-GB` folder name to your own language code, and replace all `zh` in command_helper.py to your language code.
    5. Remove everything else than `.locres` file itself, keep hierarchy.

- Convert, translate and repack
    1. Place the extracted language files into this repo's dist folder (one folder per DLC).
    2. Run:
         - `python command_helper extract`
             (converts localization files to CSV)
    3. Translate:
         - Modify translate.py by editing `TARGET_LANG` and `FILE` within the file. Ensure Google Cloud auth is active and glossary is set.
         - Run translate.py, and a new csv shows up.
    4. Merge changes:
         -  `python command_helper apply`
    5. Repack:
         -  `python command_helper pack`
    6. Testing:
        - Test this ingame, and keep your csv open to fix any mistakes.

## License

This is a modified version of WTFPL.

[DO WHAT THE FUCK YOU WANT TO IF ITS FREE PUBLIC LICENSE](./license)