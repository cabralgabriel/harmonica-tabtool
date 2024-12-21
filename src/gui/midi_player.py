import os
import mido
import tinysoundfont
from lxml import etree
from PySide6.QtCore import QUrl, QTimer
from handlers.converters import FileHandler

class MidiPlayer:
    def __init__(self, main_window):
        self.main_window = main_window
        self.frameview = main_window.frameview
        self.file_path = main_window.file_path
        self.file_name = main_window.file_name
        self.temp_dir = main_window.temp_dir
        self.mei_data = main_window.mei_data

        self.note_elements = []
        self.note_times = []
        self.note_numbers = []
        self.current_note_index = 0

        self.synth = tinysoundfont.Synth()
        soundfont_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'soundfont', 'florestan-piano.sf2'))
        self.sfid = self.synth.sfload(soundfont_path)
        self.synth.program_select(0, self.sfid, 0, 0)
        self.synth.start()

        self.file_handler = FileHandler(self)

    def play_midi(self):
        """
        Start playing the MIDI file and highlight notes in the SVG sheet music.

        This method generates a MIDI file from MEI data, extracts note information,
        loads the SVG sheet music, and starts a timer to highlight notes in sync with the music.
        """
        self.svg_sheets = os.path.join(self.temp_dir, f"{self.file_name}.svg")
        self.midi_path = self.file_handler.mei_to_midi(self.mei_data)

        if self.midi_path:
            self.note_numbers, self.note_times = self.extract_notes(self.midi_path)
            self.load_svg()

            self.timer = QTimer()
            self.timer.timeout.connect(self.highlight_next_note)
            self.timer.start(100)

    def stop_midi(self):
        """
        Stop the MIDI playback and reset the SVG highlighting.

        This method stops the MIDI playback, resets the note highlighting,
        and updates the SVG sheet music.
        """
        self.main_window.toggle_menus(True)
        self.main_window.midi_button_stop.setEnabled(False)

        if self.synth:
            self.synth.stop()
            self.synth.start()

        #if self.timer:
        #    self.timer.stop()
        self.timer = None

        if self.note_elements:
            try:
                if self.current_note_index > 0:
                    previous_note = self.note_elements[self.current_note_index - 1]
                    previous_note.set('style', self.remove_fill_style(previous_note.get('style', '')))
                if self.current_note_index < len(self.note_elements):
                    current_note = self.note_elements[self.current_note_index]
                    current_note.set('style', self.remove_fill_style(current_note.get('style', '')))
            except Exception as e:
                pass

        self.update_svg()

    def play_notes(self, note, volume=100):
        self.synth.noteon(0, note, volume)
        self.synth.noteoff(0, note)

    def load_svg(self):
        with open(self.svg_sheets, 'r') as file:
            svg_string = file.read()

        namespaces = {'svg': 'http://www.w3.org/2000/svg'}
        self.root = etree.fromstring(svg_string)
        self.note_elements = self.root.findall(".//svg:g[@class='note']", namespaces)
        self.current_note_index = 0

    def extract_notes(self, midi_file_path):
        mid = mido.MidiFile(midi_file_path)
        notes_times = []
        notes_midi = []
        current_time = 0

        for msg in mid:
            current_time += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                notes_midi.append(msg.note)
                notes_times.append((msg.note, current_time))

        return notes_midi, notes_times

    def highlight_next_note(self):
        if self.current_note_index > 0:
            previous_note = self.note_elements[self.current_note_index - 1]
            previous_note.set('style', self.remove_fill_style(previous_note.get('style', '')))

        if self.current_note_index < len(self.note_elements):
            current_note = self.note_elements[self.current_note_index]
            current_note.set('style', self.add_fill_style(current_note.get('style', ''), (255, 0, 0)))

            self.update_svg()
            if self.current_note_index < len(self.note_numbers):
                self.play_notes(self.note_numbers[self.current_note_index])
            else:
                self.stop_midi()

            # Calculate the delay for the next note based on timing
            if self.current_note_index < len(self.note_times) - 1:
                current_time = self.note_times[self.current_note_index][1]
                next_time = self.note_times[self.current_note_index + 1][1]
                time_interval = next_time - current_time
                delay = time_interval * 1000
                self.timer.start(delay)

            self.current_note_index += 1

    def add_fill_style(self, style, color):
        """
        Add a fill style to an SVG element's existing style.

        Parameters
        ----------
        style : str
            The current style string of the SVG element.
        color : tuple of int
            The RGB color values to add to the style (e.g., (255, 0, 0) for red).

        Returns
        -------
        new_style : str
            The updated style string with the fill color added.
        """
        fill_style = f'fill: rgb({color[0]}, {color[1]}, {color[2]})'

        if 'fill' in style:
            new_style_parts = []
            style_parts = style.split(';')

            for part in style_parts:
                stripped_part = part.strip()
                if 'fill' not in stripped_part:
                    new_style_parts.append(stripped_part)
            new_style_parts.append(fill_style)
            new_style = '; '.join(new_style_parts)

        else:
            if style:
                new_style = f'{style}; {fill_style}'
            else:
                new_style = fill_style

        return new_style

    def remove_fill_style(self, style):
        """
        Remove the fill style from an SVG element's style.

        Parameters
        ----------
        style : str
            The current style string of the SVG element.

        Returns
        -------
        new_style : str
            The updated style string with the fill color removed.
        """
        if 'fill' in style:
            new_style_parts = []
            style_parts = style.split(';')

            for part in style_parts:
                stripped_part = part.strip()
                if 'fill' not in stripped_part:
                    new_style_parts.append(stripped_part)
            new_style = '; '.join(new_style_parts).strip()
        else:
            new_style = style

        return new_style

    def update_svg(self):
        svg_string = etree.tostring(self.root, encoding='unicode', xml_declaration=False)
        with open(self.svg_sheets, 'w', encoding='utf-8') as file:
            file.write(svg_string)
        url = QUrl.fromLocalFile(self.svg_sheets)
        self.frameview.load(url)
