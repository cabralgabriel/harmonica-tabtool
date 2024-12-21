from cx_Freeze import setup, Executable
import os

def include_assets(assets_dir):
    return [(assets_dir, os.path.join("", os.path.basename(assets_dir)))]

build_exe_options = {
    "packages": [
        "PySide6",
        "music21",
        "verovio",
        "mido",
        "pyaudio",
        "tinysoundfont",
        "svg_stack",
        "lxml",
        "bs4",
    ],
    "excludes": [],
    "include_files": include_assets("assets"),
    "optimize": 2,
}

setup(
    name="pyHarmonica-TabTool",
    version="0.2.0",
    options={"build_exe": build_exe_options},
    executables=[Executable("src/main.py", base="Win32GUI")]
)
