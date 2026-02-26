import os
import sys


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
elif command == "extract":
    folder_list = os.listdir("./original/TS2Prototype/Plugins/DLC")
    for folder_name in folder_list:
        packname = folder_name
        path = f"original\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\en-GB\\{packname}.locres"
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
elif command == "pack":
    result = os.system(f"repak pack ./dist/ ./ZHLoc.pak --version V11")
    if result != 0:
        print(f"Error packing ZHLoc.pak. You need repak installed.")
    else:
        print(f"Successfully packed ZHLoc.pak")
elif command == "pack-riviera":
    result = os.system(f"repak pack ./riviera_patch/ ./ZHLoc-riviera-fix.pak --version V11")
    if result != 0:
        print(f"Error packing ZHLoc-riviera-fix.pak. You need repak installed.")
    else:
        print(f"Successfully packed ZHLoc-riviera-fix.pak")
else:
    print("Usage: python command_helper.py [apply|extract|pack|pack-riviera]")