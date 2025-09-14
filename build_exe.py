import PyInstaller.__main__
import os

# --- Configuration ---
script_to_bundle = 'main.py'
app_name = 'Nasikh'
icon_file = 'nasikh_icon.ico'
additional_files = [
    'src',
    icon_file
]

# --- Build the argument list for PyInstaller ---
pyinstaller_args = [
    '--onefile',
    '--windowed',
    f'--name={app_name}',
    f'--icon={icon_file}',
]

for file in additional_files:
    if os.path.isdir(file):
        pyinstaller_args.append(f'--add-data={file}{os.pathsep}{file}')
    elif os.path.isfile(file):
        pyinstaller_args.append(f'--add-data={file}{os.pathsep}.')

# Add the main script to the end of the arguments
pyinstaller_args.append(script_to_bundle)

# --- Run PyInstaller ---
if __name__ == '__main__':
    print(f"Running PyInstaller with args: {pyinstaller_args}")
    PyInstaller.__main__.run(pyinstaller_args)
    print("\n✅ Build complete.")