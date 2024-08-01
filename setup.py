
setup(
    name="MidiHarp",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "mido",
        "music21",
        "tkinter",
    ],
    entry_points={
        "console_scripts": [
            "harpviz=main:main",
        ],
    },
)
