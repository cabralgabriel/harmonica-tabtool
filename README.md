<h1 align="center">
  <br>
  <img src="https://raw.githubusercontent.com/cabralgabriel/harmonica-tabtool/main/assets/harmonica-tabtool-icon.png" alt="Harmonica TabTool" width="100">
  <br>
  Harmonica TabTool
  <br>
</h1>

<p align="center">
  <a href="">
      <img src="https://img.shields.io/badge/status-beta-blue" alt="Status: Beta">
  </a>
  <a href="https://github.com/cabralgabriel/harmonica-tabtool?tab=MIT-1-ov-file">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License: MIT">
  </a>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#install">Install</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/cabralgabriel/harmonica-tabtool/main/assets/harmonica-tabtool.gif" alt="Screenshot">
</p>

---

## Features

- **Graphical Interface**: No external tools like MuseScore or LilyPond are required.
- **Sheet Music**: Reads MusicXML and MIDI files and displays them as sheet music.
- **Harmonica Tablature**: Converts notes to standard harmonica tablature and shows it below the sheet music.
- **MIDI Preview**: Plays MIDI files with note sounds and highlights notes in red.
- **Harmonica Options**: Select between Diatonic and Chromatic harmonicas and choose different tuning types.
- **Sheet Music Tools**: Extract melody lines, reduce chords to the tonic, and show or hide keys with bends, overblows, or missing notes.
- **Export Options**: Save as MusicXML, PDF, or copy tablature to clipboard.

---

## Install

From your command line:

```bash
# Clone the repository
$ git clone https://github.com/cabralgabriel/harmonica-tabtool

# Navigate to the repository
$ cd harmonica-tabtool

# Create and activate a virtual environment
$ python -m venv env
$ source env/bin/activate  # macOS/Linux
$ .\env\Scripts\activate  # Windows

# Install dependencies
$ pip install -r requirements.txt

# Navigate to the src directory and run the app
$ cd src
$ python main.py
