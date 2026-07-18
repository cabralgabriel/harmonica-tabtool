import os
from PySide6.QtCore import QUrl

from handlers.converters import FileHandler
from handlers.score import ScoreEditor

class SheetViewer:
    def __init__(self, main_window):
        self.main_window = main_window
        self.frameview = main_window.frameview
        self.temp_dir = main_window.temp_dir
        self.file_path = main_window.file_path
        self.file_name = main_window.file_name

        self.harmonica_type = main_window.harmonica_type
        self.harmonica_tuning = main_window.harmonica_tuning
        self.harmonica_key_options = main_window.harmonica_key_options

        self.file_handler = FileHandler(self.file_path, self.file_name, self.temp_dir)
        self.score_editor = ScoreEditor()

    def get_score(self, first_use, choose_part):
        """
        Load the musical score based on the use context.

        Parameters
        ----------
        first_use : bool
            If True, load the first part. If False, use the selected part.
        choose_part : QComboBox
            Widget for selecting the musical part (degree symbol "°" is removed).

        Returns
        -------
        None
            Updates `self.piece` and `self.parts_num`.
        """
        selected_part = 1 if first_use else int(choose_part.currentText().rstrip("°"))
        
        self.piece, self.parts_num = self.file_handler.midi_to_musicxml(selected_part)

    def update_key_options(self, tabs_with_bend, tabs_with_overblow, tabs_with_missing_notes, harmonica_key, key_index, key_options_copy):
        """
        Update harmonica key options based on the current settings.

        Parameters
        ----------
        tabs_with_bend : QAction
            Action for including bends in tablature.
        tabs_with_overblow : QAction
            Action for including overblows in tablature.
        tabs_with_missing_notes : QAction
            Action for including missing notes in tablature.
        harmonica_key : QComboBox
            Combo box to select the harmonica key.
        key_index : int
            Current index of the harmonica key.
        key_options_copy : list of tuples
            Copy of the harmonica key options.

        Returns
        -------
        int
            Updated index of the harmonica key.
        """
        if self.harmonica_type.currentText() != 'Diatonic':
            return key_index
        
        self.harmonica_key_options = key_options_copy.copy()
        
        filters = [
            (tabs_with_bend.isChecked(), '\''),
            (tabs_with_overblow.isChecked(), 'o'),
            (tabs_with_missing_notes.isChecked(), '?')
        ]

        for should_filter, char in filters:
            if not should_filter:
                self.harmonica_key_options = self.score_editor.filter_keys(
                    self.piece, 
                    self.harmonica_tuning.currentText(), 
                    self.harmonica_key_options, 
                    char
                )
        
        harmonica_key.blockSignals(True)
        harmonica_key.clear()
        for key, value in self.harmonica_key_options:
            harmonica_key.addItem(key, value)
        
        harmonica_key.setCurrentIndex(max(0, min(key_index, harmonica_key.count() - 1)))
        harmonica_key.blockSignals(False)
        
        return harmonica_key.currentIndex()

    def update_sheets_viewer(self, key_index, reduce_chords):
        """
        Update the sheet music viewer with the selected options.

        Parameters
        ----------
        key_index : int
            Index of the harmonica key to use.
        reduce_chords : QCheckBox
            Checkbox to determine if chords should be reduced.

        Returns
        -------
        dict
            Dictionary with score information:
            - 'tab_in_text': str
                Tablature in text format.
            - 'parts_num': int
                Number of parts in the score.
            - 'removed_chords': list
                List of removed chords.
            - 'removed_notes': list
                List of removed notes.
            - 'mei_data': str
                MEI data as a string.
        """
        if not self.harmonica_key_options:
            self.load_default_scene()
            return {}

        self.piece = self.score_editor.edit_metadata(
            self.piece, 
            self.file_name, 
            self.harmonica_key_options[key_index][0]
        )
        
        if reduce_chords.isChecked():
            self.piece, self.removed_chords, self.removed_notes = self.score_editor.chords_handler(self.piece)

        self.piece, self.tab_in_text = self.score_editor.label_notes(
            self.piece, 
            self.harmonica_type.currentText(), 
            self.harmonica_tuning.currentText(), 
            self.harmonica_key_options[key_index][1],
            reduce_chords
        )

        # Load all sheets page
        self.svgs_pages, self.mei_data = self.file_handler.musicxml_to_svg(self.piece)

        # Convert to a full long page
        self.svg_sheets = self.svg_html_stacker(self.svgs_pages)

        # Load .html sheets
        self.display_sheets_file()
        
        return {
            'tab_in_text': self.tab_in_text,
            'parts_num': self.parts_num,
            'removed_chords': self.removed_chords,
            'removed_notes': self.removed_notes,
            'mei_data': self.mei_data
        }
    

    def svg_html_stacker(self, svg_pages):

        sheets_pages = []
        for svg in svg_pages:
            sheets_pages.append(f'<div class="page">{svg}</div>')
        full_sheet = '\n'.join(sheets_pages)

        # Read template (needs to add a option to select sheet layout)
        sheets_template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'sheets_layout', 'template.html'))
        with open(sheets_template_path, 'r', encoding='utf-8') as f:
            sheets_template_path = f.read()

        # Stack all svg
        self.sheets_string = sheets_template_path.replace('{{sheets}}', full_sheet)
        
        # Write temp file because is more faster load a .html
        self.sheets_path = os.path.join(self.temp_dir, f"{self.file_name}_preview.html")
        with open(self.sheets_path, 'w', encoding='utf-8') as f:
            f.write(self.sheets_string)

        return self.sheets_path
    
    # This is more faster than using setHtml() or setContent()
    def display_sheets_file(self):
        if self.svg_sheets:
            svgs_url = QUrl.fromLocalFile(self.svg_sheets)
            self.frameview.load(svgs_url)

    def load_default_scene(self):
        nokeys = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'screens', 'nokeys.html'))
        nokeys_url = QUrl.fromLocalFile(nokeys)
        self.frameview.load(nokeys_url)

