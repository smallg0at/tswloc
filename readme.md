# Train Sim World DLC Chinese Translation

[简体中文](./readme_zh.md)

Because the official localization team cannot handle up to 17 third‑party DLCs on the route map and only provides English and German, I did the translations by myself. This repository contains all the original translation source files.

Currently localized DLCs:

- ✅ Birmingham Cross‑City Line — Class 170 (Rivet Games)
- ✅ West Coast Main Line: Birmingham–Crewe (AABS)

## Installation

Steam: place the .pak file into `<Documents>\My Games\TrainSimWorld6\Saved\UserContent`.
Epic: place the .pak file into `<Documents>\My Games\TrainSimWorld6EGS\Saved\UserContent`.

## Development

You need unpak and a Google Cloud account. First use unpak to extract the language files, then put them in this repo's dist folder. Next, run `command_helper export` to convert to CSV, use `translate.py` to translate (adjust the glossary `glossary.csv` and get your Google Cloud account authenticated first!), then run `command_helper apply` to merge changes, and finally `command_helper pack` to repack.
