import os
import shutil
import sys
import winreg


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
    file_list = os.listdir('.')
    target_list = [f for f in file_list if f.endswith('_translated.csv')]
    for file_name in target_list:
        packname = file_name.replace('_translated.csv','')
        path = f"dist\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\zh\\{packname}.locres"
        command = f'.\\Utils\\UnrealLocres.exe import "{path}" "{file_name}" -f csv -o "{path}"'
        result = os.system(command)
        if result != 0:
            input(f"⚠ Error applying translation for {packname}, Enter to continue...")
        else:
            print(f"Successfully applied translation for {packname}")
# if command == "apply145":
#     # Apply all back
#     # usage: UnrealLocres.exe import locres_file_path translation_file_path [-f {csv,pot}] [-o output_path]
#     file_list = os.listdir('.')
#     target_list = [f for f in file_list if f.endswith('145pack_translated.csv')]
#     for file_name in target_list:
#         packname = file_name.replace('.145pack_translated.csv','')
#         path = f"dist_145pack\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\zh\\{packname}.locres"
#         command = f'.\\Utils\\UnrealLocres.exe import "{path}" "{file_name}" -f csv -o "{path}"'
#         result = os.system(command)
#         if result != 0:
#             input(f"⚠ Error applying translation for {packname}, Enter to continue...")
#         else:
#             print(f"Successfully applied translation for {packname}")
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
        output_file = f"{packname}.locres.csv"
        if os.path.exists(output_file):
            print(f"Translation file for {packname} already exists, skipping extraction.")
            continue
        command = f'.\\Utils\\UnrealLocres.exe export "{path}" -o "{output_file}" -f csv'
        result = os.system(command)
        if result != 0:
            print(f"Error extracting translation for {packname}")
        else:
            print(f"Successfully extracted translation for {packname}")
# elif command == "extract145":
#     folder_list = os.listdir("./original_145pack/TS2Prototype/Plugins/DLC")
#     for folder_name in folder_list:
#         packname = folder_name
#         path1 = f"original_145pack\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\en-GB\\{packname}.locres"
#         path2 = f"original_145pack\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\en\\{packname}.locres"
#         path = path1 if os.path.exists(path1) else path2
#         if not os.path.exists(path):
#             print(f"Source file for {packname} not found, skipping.")
#             continue
#         output_file = f"{packname}.145pack.locres.csv"
#         if os.path.exists(output_file):
#             print(f"Translation file for {packname} already exists, skipping extraction.")
#             continue
#         command = f'.\\Utils\\UnrealLocres.exe export "{path}" -o "{output_file}" -f csv'
#         result = os.system(command)
#         if result != 0:
#             print(f"Error extracting translation for {packname}")
#         else:
#             print(f"Successfully extracted translation for {packname}")
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
# elif command == "pack-145":
#     result = os.system(f"repak pack ./dist_145pack/ ./ZHLoc-145.pak --version V11")
#     if result != 0:
#         print(f"Error packing ZHLoc-145.pak. You need repak installed.")
#     else:
#         print(f"Successfully packed ZHLoc-145.pak")
elif command == "pack-riviera":
    result = os.system(f"repak pack ./riviera_patch/ ./ZHLoc-riviera-fix.pak --version V11")
    if result != 0:
        print(f"Error packing ZHLoc-riviera-fix.pak. You need repak installed.")
    else:
        print(f"Successfully packed ZHLoc-riviera-fix.pak")
else:
    print("Usage: python command_helper.py [apply|extract|pack|pack-riviera]")
