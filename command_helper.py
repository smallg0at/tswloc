import os
import shutil
import subprocess
import sys
import re
from pathlib import Path
import winreg
from merge import merge_csvs


LOCRES_PATH_RE = re.compile(
    r"^(?P<root>TS2Prototype[\\/]Plugins[\\/]DLC[\\/])"
    r"(?P<pack>[^\\/]+)[\\/]Content[\\/]Localization[\\/]"
    r"(?P<locpack>[^\\/]+)[\\/](?P<locale>en-GB|en|zh-CN|zh)[\\/]"
    r"(?P<file>[^\\/]+\.locres)$"
)


def list_locres_paths(pak_file, locales):
    result = subprocess.run(
        ["repak", "list", str(pak_file)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "repak list failed")

    paths = []
    for line in result.stdout.splitlines():
        path = line.strip().replace("\\", "/")
        match = LOCRES_PATH_RE.match(path)
        if match and match.group("locale") in locales:
            paths.append((path, match.groupdict()))
    return paths


def unpack_locres(pak_file, output_dir, locales):
    paths = list_locres_paths(pak_file, locales)
    if not paths:
        raise RuntimeError("No matching localization locres files found in the pak")

    args = ["repak", "unpack", str(pak_file), "-o", str(output_dir)]
    for path, _ in paths:
        args.extend(["--include", path])
    result = subprocess.run(args, check=False)
    if result.returncode != 0:
        raise RuntimeError("repak unpack failed")
    return paths


def export_and_merge(packname, source_path, localized_path, output_file):
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    source_csv = temp_dir / f"{packname}.en.csv"
    localized_csv = temp_dir / f"{packname}.zh.csv"
    export_source = f'.\\Utils\\UnrealLocres.exe export "{source_path}" -o "{source_csv}" -f csv'
    export_localized = f'.\\Utils\\UnrealLocres.exe export "{localized_path}" -o "{localized_csv}" -f csv'
    if os.system(export_source) != 0 or os.system(export_localized) != 0:
        return False
    merge_csvs(str(source_csv), str(localized_csv), str(output_file))
    return True


def repository_path(root, pak_path, source_locale=None, target_locale=None):
    parts = pak_path.replace("\\", "/").split("/")
    if source_locale and target_locale:
        parts[parts.index(source_locale)] = target_locale
    return Path(root, *parts)


def choose_packs(pack_paths):
    available = []
    for packname, paths in sorted(pack_paths.items()):
        locales = {metadata["locale"] for _, metadata in paths}
        if ({"en", "en-GB"} & locales) and ({"zh", "zh-CN"} & locales):
            available.append(packname)

    if not available:
        print("No packs containing both English and Chinese locres were found.")
        return set()

    print("Packs available for import:")
    for index, packname in enumerate(available, 1):
        print(f"  {index}. {packname}")
    print("Enter numbers separated by commas, 'all' for every pack, or 'q' to cancel.")
    selection = input("Import: ").strip().lower()
    if selection in {"", "q", "quit", "cancel"}:
        print("Import cancelled.")
        return set()
    if selection == "all":
        return set(available)

    selected = set()
    for value in selection.split(","):
        value = value.strip()
        if value.isdigit() and 1 <= int(value) <= len(available):
            selected.add(available[int(value) - 1])
        else:
            print(f"Ignoring invalid selection: {value}")
    return selected

def get_documents_path():
    """Resolve the real Documents folder on Windows (not always under %USERPROFILE%)."""
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            personal, _ = winreg.QueryValueEx(key, "Personal")
            if isinstance(personal, str) and personal:
                return os.path.expandvars(personal)
    except OSError:
        pass

    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            personal, _ = winreg.QueryValueEx(key, "Personal")
            if isinstance(personal, str) and personal:
                return personal
    except OSError:
        pass

    # Fallback when registry keys are unavailable.
    return os.path.join(os.path.expanduser("~"), "Documents")


command = ''
if len(sys.argv) > 1:
    command = sys.argv[1].lower()


if command == "update":
    if len(sys.argv) != 3:
        print("Usage: python command_helper.py update <updated-DLC.pak>")
        sys.exit(1)
    try:
        pak_file = sys.argv[2]
        paths = unpack_locres(pak_file, "original", {"en", "en-GB"})
        processed = set()
        for pak_path, metadata in paths:
            packname = metadata["pack"]
            if packname in processed or packname == "Foob_GodMode":
                continue
            processed.add(packname)
            source_path = repository_path("original", pak_path)
            localized_path = repository_path(
                "dist", pak_path, metadata["locale"], "zh"
            )
            csv_file = Path("csv", f"{packname}_translated.csv")
            if not csv_file.exists() or not localized_path.exists():
                print(f"No existing translated CSV/dist file for {packname}, skipping.")
                continue
            if export_and_merge(packname, source_path, localized_path, csv_file):
                shutil.copy2(source_path, localized_path)
                print(f"Updated {packname}; new rows are marked TBT.")
            else:
                print(f"Error updating {packname}; old dist file was kept.")
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Update failed: {exc}")
        sys.exit(1)
elif command == "import-localized":
    if len(sys.argv) != 3:
        print("Usage: python command_helper.py import-localized <localized-DLC.pak>")
        sys.exit(1)
    import_dir = Path("temp", "import-localized")
    try:
        if import_dir.exists():
            shutil.rmtree(import_dir)
        paths = unpack_locres(
            sys.argv[2], import_dir, {"en", "en-GB", "zh", "zh-CN"}
        )
        by_pack = {}
        for pak_path, metadata in paths:
            by_pack.setdefault(metadata["pack"], []).append((pak_path, metadata))

        selected_packs = choose_packs(by_pack)
        for packname, pack_paths in by_pack.items():
            if packname not in selected_packs:
                continue
            source = next(
                (item for item in pack_paths if item[1]["locale"] == "en"),
                next(
                    (item for item in pack_paths if item[1]["locale"] == "en-GB"),
                    None,
                ),
            )
            localized = next(
                (item for item in pack_paths if item[1]["locale"] == "zh"),
                next(
                    (item for item in pack_paths if item[1]["locale"] == "zh-CN"),
                    None,
                ),
            )
            if not source or not localized:
                print(f"Both English and Chinese locres not found for {packname}, skipping.")
                continue

            source_path = repository_path("original", source[0])
            localized_path = repository_path(
                "dist", localized[0], localized[1]["locale"], "zh"
            )
            extracted_source = repository_path(import_dir, source[0])
            extracted_localized = repository_path(import_dir, localized[0])
            source_path.parent.mkdir(parents=True, exist_ok=True)
            localized_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(extracted_source, source_path)
            shutil.copy2(extracted_localized, localized_path)

            csv_file = Path("csv", f"{packname}_translated.csv")
            if export_and_merge(packname, source_path, localized_path, csv_file):
                print(f"Imported localized DLC {packname} into original/dist/csv.")
            else:
                print(f"Error exporting localized DLC {packname}; files were copied.")
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Localized DLC import failed: {exc}")
        sys.exit(1)
    finally:
        if import_dir.exists():
            shutil.rmtree(import_dir)
elif command == "apply":
    # Apply all back
    # usage: UnrealLocres.exe import locres_file_path translation_file_path [-f {csv,pot}] [-o output_path]
    file_list = os.listdir('./csv/')
    target_list = [f for f in file_list if f.endswith('_translated.csv')]
    for file_name in target_list:
        packname = file_name.replace('_translated.csv','')
        path = f"dist\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\zh\\{packname}.locres"
        command = f'.\\Utils\\UnrealLocres.exe import "{path}" "./csv/{file_name}" -f csv -o "{path}"'
        result = os.system(command)
        if result != 0:
            input(f"⚠ Error applying translation for {packname}, Enter to continue...")
        else:
            print(f"Successfully applied translation for {packname}")
elif command == "extract":
    folder_list = os.listdir("./original/TS2Prototype/Plugins/DLC")
    for folder_name in folder_list:
        packname = folder_name
        path1 = f"original\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\en-GB\\{packname}.locres"
        path2 = f"original\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\en\\{packname}.locres"
        path = path1 if os.path.exists(path1) else path2
        # skip godmode also.
        if packname == "Foob_GodMode":
            print(f"Skipping {packname}")
            continue
        if not os.path.exists(path):
            print(f"Source file for {packname} not found, skipping.")
            continue
        output_file = f"./csv/{packname}.locres.csv"
        # if os.path.exists(output_file):
        #     print(f"Translation file for {packname} already exists, skipping extraction.")
        #     continue
        command = f'.\\Utils\\UnrealLocres.exe export "{path}" -o "{output_file}" -f csv'
        result = os.system(command)
        if result != 0:
            print(f"Error extracting translation for {packname}")
        else:
            print(f"Successfully extracted translation for {packname}")
elif command == "pack":
    result = os.system(
        f"repak pack ./dist/ ./ZHLoc.pak --version V11  --compression Zlib"
    )
    if result != 0:
        print(f"Error packing ZHLoc.pak. You need repak installed.")
    else:
        print(f"Successfully packed ZHLoc.pak")
        # Copy the packed .pak to TSW6 UserContent.
        source_file = os.path.abspath("./ZHLoc.pak")
        documents_dir = get_documents_path()
        user_content_dir = os.path.join(
            documents_dir, "My Games", "TrainSimWorld7", "Saved", "UserContent"
        )
        target_file = os.path.join(user_content_dir, "ZHLoc.pak")

        try:
            os.makedirs(user_content_dir, exist_ok=True)
            shutil.copy2(source_file, target_file)
            print(f"Successfully copied ZHLoc.pak to \"{user_content_dir}\"")
        except Exception as exc:
            print(
                f"Error copying ZHLoc.pak to UserContent folder ({user_content_dir}): {exc}"
            )
            print(
                f"Please copy it manually from {source_file} to {user_content_dir}"
            )
elif command == "pack-riviera":
    result = os.system(f"repak pack ./riviera_patch/ ./ZHLoc-riviera-fix.pak --version V11")
    if result != 0:
        print(f"Error packing ZHLoc-riviera-fix.pak. You need repak installed.")
    else:
        print(f"Successfully packed ZHLoc-riviera-fix.pak")
elif command == "godmode-apply":
    # Apply godmode translation
    packname = "Foob_GodMode"
    csv_file = f"./csv/csv_godmode/{packname}_translated.csv"
    if not os.path.exists(csv_file):
        print(f"Translation file {csv_file} not found.")
    else:
        path = f"dist_godmode\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\zh\\{packname}.locres"
        command_str = f'.\\Utils\\UnrealLocres.exe import "{path}" "{csv_file}" -f csv -o "{path}"'
        result = os.system(command_str)
        if result != 0:
            input(f"⚠ Error applying translation for {packname}, Enter to continue...")
        else:
            print(f"Successfully applied translation for {packname}")
elif command == "godmode-extract":
    # Find godmode's en and zh locres, extract them both and merge, preferring zh translation if en text matches.
    packname = "Foob_GodMode"
    path_en1 = f"original\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\en-GB\\{packname}.locres"
    path_en2 = f"original\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\en\\{packname}.locres"
    path_zh = f"dist_godmode\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\zh\\{packname}.locres"
    path_en = path_en2 if os.path.exists(path_en2) else path_en1
    if not os.path.exists(path_en) or not os.path.exists(path_zh):
        print(f"Source files for {packname} not found.")
    else:
        output_file = f"./csv/csv_godmode/{packname}_translated.csv"
        do_merge = True
        if os.path.exists(output_file):
            do_merge = (
                input(
                    f"Merged translation file for {packname} exists. Do merge for {packname}? (y/N) "
                ).lower()
                == "y"
            )
        if do_merge:
            command_en = f'.\\Utils\\UnrealLocres.exe export "{path_en}" -o "./temp/{packname}.en.csv" -f csv'
            command_zh = f'.\\Utils\\UnrealLocres.exe export "{path_zh}" -o "./temp/{packname}.zh.csv" -f csv'
            result_en = os.system(command_en)
            result_zh = os.system(command_zh)
            if result_en != 0 or result_zh != 0:
                print(f"Error extracting translation for {packname}")
            else:
                merge_csvs(f"./temp/{packname}.en.csv", f"./temp/{packname}.zh.csv", output_file)
                print(f"Successfully merged translation for {packname}")
elif command == "godmode-override":
    # override godmode's source english locres into dist_godmode, rebuilding its key structure
    # so a subsequent godmode-apply can write newly added keys (see "override" for the non-godmode equivalent).
    packname = "Foob_GodMode"
    path_en1 = f"original\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\en-GB\\{packname}.locres"
    path_en2 = f"original\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\en\\{packname}.locres"
    path_zh = f"dist_godmode\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\zh\\{packname}.locres"
    path_en = path_en2 if os.path.exists(path_en2) else path_en1
    if not os.path.exists(path_en):
        print(f"Source files for {packname} not found.")
    else:
        if not os.path.exists(path_zh):
            os.makedirs(os.path.dirname(path_zh), exist_ok=True)
        command_override = f'copy "{path_en}" "{path_zh}" /Y'
        result_override = os.system(command_override)
        if result_override != 0:
            print(f"Error overriding english locres for {packname}")
        else:
            print(f"Successfully overridden english locres for {packname}")
elif command == "godmode-pack":
    result = os.system(f"repak pack ./dist_godmode/ ./ZHLoc-GodMode.pak --version V11")
    if result != 0:
        print(f"Error packing ZHLoc-GodMode.pak. You need repak installed.")
    else:
        print(f"Successfully packed ZHLoc-GodMode.pak")
        # Copy the packed .pak to TSW6 UserContent.
        source_file = os.path.abspath("./ZHLoc-GodMode.pak")
        documents_dir = get_documents_path()
        user_content_dir = os.path.join(
            documents_dir, "My Games", "TrainSimWorld7", "Saved", "UserContent"
        )
        target_file = os.path.join(user_content_dir, "ZHLoc-GodMode.pak")

        try:
            os.makedirs(user_content_dir, exist_ok=True)
            shutil.copy2(source_file, target_file)
            print(f"Successfully copied ZHLoc-GodMode.pak to \"{user_content_dir}\"")
        except Exception as exc:
            print(
                f"Error copying ZHLoc-GodMode.pak to UserContent folder ({user_content_dir}): {exc}"
            )
            print(
                f"Please copy it manually from {source_file} to {user_content_dir}"
            )
elif command == "merge":
    # Find a pack with both en and zh locres, extract them all and add the missing translation from zh version.
    folder_list = os.listdir("./original/TS2Prototype/Plugins/DLC")
    for folder_name in folder_list:
        packname = folder_name
        path_en1 = f"original\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\en-GB\\{packname}.locres"
        path_en2 = f"original\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\en\\{packname}.locres"
        path_zh = f"dist\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\zh\\{packname}.locres"
        path_en = path_en2 if os.path.exists(path_en2) else path_en1
        if not os.path.exists(path_en) or not os.path.exists(path_zh):
            print(f"Source files for {packname} not found, skipping.")

        output_file = f"{packname}"
        if "CRG" in packname:
            # Skip BR145
            continue
        if os.path.exists(f"./csv/{output_file}_translated.csv"):
            if (
                input(
                    f"Merged translation file for {packname} exists. Do merge for {packname}? (y/N) "
                ).lower()
                != "y"
            ):
                continue
        else:
            print(f"target file for {packname} not found.")
            continue
        # extract them separately and merge the results
        command_en = f'.\\Utils\\UnrealLocres.exe export "{path_en}" -o "./temp/{output_file}.en.csv" -f csv'
        command_zh = f'.\\Utils\\UnrealLocres.exe export "{path_zh}" -o "./temp/{output_file}.zh.csv" -f csv'
        result_en = os.system(command_en)
        result_zh = os.system(command_zh)
        if result_en != 0 or result_zh != 0:
            print(f"Error extracting translation for {packname}")
            continue
        # call merge.pymerge the two csv files, prefer zh translation if en text matches
        merge_csvs(f"./temp/{output_file}.en.csv", f"./temp/{output_file}.zh.csv", f"./csv/{output_file}_translated.csv")
        print(f"Successfully merged translation for {packname}")
elif command == "override":
    # override all source english file to respective place for dist to merge stuff
    # We need the target file to exist.
    folder_list = os.listdir("./original/TS2Prototype/Plugins/DLC")
    for folder_name in folder_list:
        packname = folder_name
        path_en1 = f"original\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\en-GB\\{packname}.locres"
        path_en2 = f"original\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\en\\{packname}.locres"
        path_zh = f"dist\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\zh\\{packname}.locres"
        path_en = path_en2 if os.path.exists(path_en2) else path_en1
        # skip godmode, it uses a separate dist_godmode tree (see godmode-override).
        if packname == "Foob_GodMode":
            print(f"Skipping {packname}")
            continue
        if not os.path.exists(path_en):
            print(f"Source files for {packname} not found, skipping.")
            continue
        if not os.path.exists(path_zh):
            # Create the folder if not exist to avoid copy error.
            os.makedirs(os.path.dirname(path_zh), exist_ok=True)
        command_override = f'copy "{path_en}" "{path_zh}" /Y'
        result_override = os.system(command_override)
        if result_override != 0:
            print(f"Error overriding english locres for {packname}")
            continue
        print(f"Successfully overridden english locres for {packname}")
else:
    print("Usage: python command_helper.py <command>")
    print()
    print("Commands:")
    print("  update <pak>    Extract an updated DLC pak's en locres, merge existing translations, and rebuild dist keys")
    print("  import-localized <pak>  Import en+zh locres from a localized DLC pak into original/, dist/, and csv/")
    print("  extract          Export en/en-GB locres from original/ into ./csv/<PackName>.locres.csv (skips Foob_GodMode)")
    print("  apply            Import every ./csv/*_translated.csv back into dist/.../zh/<PackName>.locres")
    print("  merge            Re-export en+zh locres for a pack and merge into ./csv/<PackName>_translated.csv, preferring existing zh text over en")
    print("  override         Force-copy en/en-GB locres over the zh slot in dist/ for every pack (skips Foob_GodMode), rebuilding key structure after a DLC patch")
    print("  pack             repak dist/ into ZHLoc.pak and copy it to the TSW6 UserContent folder")
    print("  pack-riviera     repak riviera_patch/ into ZHLoc-riviera-fix.pak")
    print("  godmode-extract  Same as merge, but for the Foob_GodMode pack (original/ + dist_godmode/ -> ./csv/csv_godmode/)")
    print("  godmode-override Same as override, but for the Foob_GodMode pack (original/ -> dist_godmode/)")
    print("  godmode-apply    Import ./csv/csv_godmode/Foob_GodMode_translated.csv into dist_godmode/.../zh/Foob_GodMode.locres")
    print("  godmode-pack     repak dist_godmode/ into ZHLoc-GodMode.pak and copy it to the TSW6 UserContent folder")
