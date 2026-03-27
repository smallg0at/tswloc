import os
import shutil
import sys
import winreg
from merge import merge_csvs

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


if command == "apply":
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
        if not os.path.exists(path):
            print(f"Source file for {packname} not found, skipping.")
            continue
        output_file = f"./csv/{packname}.locres.csv"
        if os.path.exists(output_file):
            print(f"Translation file for {packname} already exists, skipping extraction.")
            continue
        command = f'.\\Utils\\UnrealLocres.exe export "{path}" -o "{output_file}" -f csv'
        result = os.system(command)
        if result != 0:
            print(f"Error extracting translation for {packname}")
        else:
            print(f"Successfully extracted translation for {packname}")
elif command == "pack":
    result = os.system(f"repak pack ./dist/ ./ZHLoc.pak --version V11")
    if result != 0:
        print(f"Error packing ZHLoc.pak. You need repak installed.")
    else:
        print(f"Successfully packed ZHLoc.pak")
        # Copy the packed .pak to TSW6 UserContent.
        source_file = os.path.abspath("./ZHLoc.pak")
        documents_dir = get_documents_path()
        user_content_dir = os.path.join(
            documents_dir, "My Games", "TrainSimWorld6", "Saved", "UserContent"
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
elif command == "merge":
    # Find a pack with both en and zh locres, extract them all and add the missing translation from zh version.
    folder_list = os.listdir("./original/TS2Prototype/Plugins/DLC")
    for folder_name in folder_list:
        packname = folder_name
        path_en1 = f"original\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\en-GB\\{packname}.locres"
        path_en2 = f"original\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\en\\{packname}.locres"
        path_zh = f"original\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\zh\\{packname}.locres"
        path_en = path_en2 if os.path.exists(path_en2) else path_en1
        if not os.path.exists(path_en) or not os.path.exists(path_zh):
            print(f"Source files for {packname} not found, skipping.")
            continue
        output_file = f"{packname}"
        if os.path.exists(f"./csv/{output_file}_translated.csv"):
            print(f"Merged translation file for {packname} already exists, skipping.")
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
else:
    print("Usage: python command_helper.py [apply|extract|pack|pack-riviera|merge]")
