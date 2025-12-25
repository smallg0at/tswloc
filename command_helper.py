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
            print(f"Error applying translation for {packname}")
        else:
            print(f"Successfully applied translation for {packname}")
elif command == "extract":
    folder_list = os.listdir("./dist/TS2Prototype/Plugins/DLC")
    for folder_name in folder_list:
        packname = folder_name
        path = f"dist\\TS2Prototype\\Plugins\\DLC\\{packname}\\Content\\Localization\\{packname}\\zh\\{packname}.locres"
        output_file = f"{packname}.locres.csv"
        command = f'.\\Utils\\UnrealLocres.exe export "{path}" -o "{output_file}" -f csv'
        result = os.system(command)
        if result != 0:
            print(f"Error extracting translation for {packname}")
        else:
            print(f"Successfully extracted translation for {packname}")
elif command == "pack":
    result = os.system("repak pack ./dist/ ./!ZHLoc.pak --version V11")
    if result != 0:
        print("Error packing !ZHLoc.pak. You need repak installed.")
    else:
        print("Successfully packed !ZHLoc.pak")
else:
    print("Usage: python command_helper.py [apply|extract|pack]")