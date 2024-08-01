import os
import shutil
import tempfile
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QFileDialog, QCheckBox, QStackedLayout, QFormLayout, QMessageBox, QStatusBar
from PySide6.QtGui import QAction, QIcon, QPageSize, QPageLayout, QGuiApplication
from PySide6.QtCore import Qt, QUrl, QByteArray, QMarginsF
from PySide6.QtWebEngineWidgets import QWebEngineView

from gui.sheet_viewer import SheetViewer
from gui.midi_player import MidiPlayer
from handlers.converters import FileHandler
from handlers.score import ScoreEditor
from handlers.tunings import TuningHandler
from handlers.svg import SVGHandler

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.create_status_bar()
        self.create_left_frame()
        self.create_right_frame()
        self.create_menu()
        self.make_temp_directory()

    def init_ui(self):
        self.setWindowTitle("Harmonica TabViewer")
        self.setGeometry(100, 100, 1280, 720)
        #self.setWindowFlags(Qt.FramelessWindowHint)

        my_icon = QIcon()
        my_icon.addFile('./assets/icon.png')
        self.setWindowIcon(QIcon(my_icon))

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.setStyleSheet("""
            QWidget {
                font-size: 14px;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #0078d7;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QLabel {
                margin-top: 10px;
                margin-bottom: 5px;
                font-weight: bold;
            }
            QComboBox {
                padding: 5px;
            }
            QCheckBox {
                margin-top: 5px;
            }
        """)

    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.status_bar.setFixedHeight(15)
        self.setStatusBar(self.status_bar)

    def create_left_frame(self):
        self.left_frame = QWidget(self.central_widget)
        self.left_layout = QVBoxLayout(self.left_frame)
        self.left_layout.setContentsMargins(10, 10, 10, 10)
        self.left_layout.setSpacing(10)
        self.left_frame.setLayout(self.left_layout)
        self.main_layout.addWidget(self.left_frame, 0.5)

        self.harmonica_type_layout = QFormLayout(self.left_frame)
        self.harmonica_type_label = QLabel("Type:")
        self.harmonica_type_layout.addRow(self.harmonica_type_label)
        self.harmonica_type_options = ["Diatonic", "Chromatic"]
        self.harmonica_type = QComboBox()
        self.harmonica_type.addItems(self.harmonica_type_options)
        self.harmonica_type.setEnabled(False)
        self.harmonica_type_layout.addRow(self.harmonica_type)
        self.harmonica_type.currentIndexChanged.connect(self.on_type_change)

        self.harmonica_tuning_layout = QFormLayout()
        self.harmonica_tuning_label = QLabel("Tuning:")
        self.harmonica_tuning_layout.addRow(self.harmonica_tuning_label)
        self.harmonica_tuning_options = ["Standard Richter", "Paddy Richter", "Melody Maker", "Country", "Natural Minor", "Wilde Rock"]
        self.harmonica_tuning = QComboBox()
        self.harmonica_tuning.addItems(self.harmonica_tuning_options)
        self.harmonica_tuning.setEnabled(False)
        self.harmonica_tuning_layout.addRow(self.harmonica_tuning)
        self.harmonica_tuning.currentIndexChanged.connect(self.on_tuning_change)

        self.harmonica_key_layout = QFormLayout()
        self.harmonica_key_label = QLabel("Key:")
        self.harmonica_key_layout.addRow(self.harmonica_key_label)
        self.harmonica_key_options = [
            ("Low G", "G2"), ("Low Ab", "Ab2"), ("Low A", "A2"), ("Low Bb", "Bb2"),
            ("Low B", "B2"), ("Low C", "C3"), ("Low C#", "C#3"), ("Low D", "D3"),
            ("Low Eb", "Eb3"), ("Low E", "E3"), ("Low F", "F3"), ("Low F#", "F#3"),
            ("G", "G3"), ("Ab", "Ab3"), ("A", "A3"), ("Bb", "Bb3"), 
            ("B", "B3"), ("C", "C4"), ("Db", "Db4"), ("D", "D4"), 
            ("Eb", "Eb4"), ("E", "E4"), ("F", "F4"), ("F#", "F#4"),
            ("High G", "G4"), ("High C", "C5")
        ]
        self.harmonica_key = QComboBox()
        for gui, _ in self.harmonica_key_options:
            self.harmonica_key.addItem(gui)
        self.harmonica_key.setEnabled(False)
        self.harmonica_key_layout.addRow(self.harmonica_key)
        self.harmonica_key.currentIndexChanged.connect(self.on_key_change)
        self.harmonica_key_index = self.harmonica_key.currentIndex()
        self.harmonica_key_options_copy = self.harmonica_key_options.copy()

        self.choose_part_layout = QFormLayout()
        self.choose_part_label = QLabel("Choose Part:")
        self.choose_part_layout.addRow(self.choose_part_label)
        self.choose_part_options = ["1°"]
        self.choose_part = QComboBox()
        self.choose_part.addItems(self.choose_part_options)
        self.choose_part.setEnabled(False)
        self.choose_part_layout.addRow(self.choose_part)
        self.choose_part.currentIndexChanged.connect(self.on_part_change)

        self.reduce_chords_layout = QFormLayout()
        self.reduce_chords_label = QLabel("Reduce Chords:")
        self.reduce_chords_layout.addRow(self.reduce_chords_label)
        self.reduce_chords = QCheckBox("On/Off")
        self.reduce_chords.setChecked(True)
        self.reduce_chords.setEnabled(False)
        self.reduce_chords.stateChanged.connect(self.on_chord_change)
        self.reduce_chords_layout.addRow(self.reduce_chords)

        self.midi_player_layout = QVBoxLayout()
        self.midi_player_label = QLabel("Preview Midi:")
        self.midi_player_layout.addWidget(self.midi_player_label)
        self.midi_buttons_layout = QHBoxLayout()
        self.midi_button_play = QPushButton("Play")
        self.midi_button_play.setEnabled(False)
        self.midi_button_play.clicked.connect(self.on_play_midi)
        self.midi_buttons_layout.addWidget(self.midi_button_play)
        self.midi_button_stop = QPushButton("Stop")
        self.midi_button_stop.setEnabled(False)
        self.midi_button_stop.clicked.connect(self.on_stop_midi)
        self.midi_buttons_layout.addWidget(self.midi_button_stop)
        self.midi_player_layout.addLayout(self.midi_buttons_layout)

        self.left_layout.addLayout(self.harmonica_type_layout)
        self.left_layout.addLayout(self.harmonica_tuning_layout)
        self.left_layout.addLayout(self.harmonica_key_layout)
        self.left_layout.addLayout(self.choose_part_layout)
        self.left_layout.addLayout(self.reduce_chords_layout)
        self.left_layout.addLayout(self.midi_player_layout)

    def create_right_frame(self):
        self.right_frame = QWidget()
        self.right_layout = QVBoxLayout(self.right_frame)
        self.right_layout.setContentsMargins(10, 10, 10, 0)
        self.right_layout.setSpacing(10)
        self.right_frame.setLayout(self.right_layout)
        self.main_layout.addWidget(self.right_frame, 2)

        self.frameview = QWebEngineView()
        start = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'start.html'))
        start_url = QUrl.fromLocalFile(start)
        self.frameview.load(start_url)
        self.frameview.setZoomFactor(0.5)
        self.frameview.setContextMenuPolicy(Qt.NoContextMenu)
        self.right_layout.addWidget(self.frameview)

    def create_menu(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("File")
        tools_menu = menubar.addMenu("Tools")
        about_menu = menubar.addMenu("Help")

        self.open_file_menu = QAction(f"Open...", self)
        self.open_file_menu.setEnabled(True)
        self.open_file_menu.triggered.connect(self.open_file)
        file_menu.addAction(self.open_file_menu)

        self.save_as_musicxml = QAction(f"Export File as .musicxml", self)
        self.save_as_musicxml.setEnabled(False)
        self.save_as_musicxml.triggered.connect(self.save_file_as_musicxml)
        file_menu.addAction(self.save_as_musicxml)

        self.print_pdf = QAction(f"Export File as .pdf", self)
        self.print_pdf.setEnabled(False)
        self.print_pdf.triggered.connect(self.save_file_as_pdf)
        file_menu.addAction(self.print_pdf)

        self.tabs_with_bend = QAction("Show Tabs with Bends", self)
        self.tabs_with_bend.setEnabled(False)
        self.tabs_with_bend.setCheckable(True) 
        self.tabs_with_bend.setChecked(True)
        self.tabs_with_bend.triggered.connect(self.toggle_tabs_with_bend)
        tools_menu.addAction(self.tabs_with_bend)

        self.tabs_with_overblow = QAction("Show Tabs with Overblows", self)
        self.tabs_with_overblow.setEnabled(False)
        self.tabs_with_overblow.setCheckable(True) 
        self.tabs_with_overblow.setChecked(True)
        self.tabs_with_overblow.triggered.connect(self.toggle_tabs_with_overblow)
        tools_menu.addAction(self.tabs_with_overblow)

        self.tabs_with_missing_notes = QAction("Show Tabs with Missing Notes", self)
        self.tabs_with_missing_notes.setEnabled(False)
        self.tabs_with_missing_notes.setCheckable(True) 
        self.tabs_with_missing_notes.setChecked(True)
        self.tabs_with_missing_notes.triggered.connect(self.toggle_tabs_with_missing_notes)
        tools_menu.addAction(self.tabs_with_missing_notes)

        self.copy_tab_to_clipboard = QAction("Copy Tab to Clipboard", self)
        self.copy_tab_to_clipboard.setEnabled(False)
        self.copy_tab_to_clipboard.triggered.connect(self.copy_to_clipboard)
        tools_menu.addAction(self.copy_tab_to_clipboard)

        self.harp_keys = QAction("Chart: Harp Keys", self)
        self.harp_keys.setEnabled(True)
        self.harp_keys.triggered.connect(self.open_harp_keys)
        about_menu.addAction(self.harp_keys)

        self.tab_rulers = QAction("Chart: Tab Rulers", self)
        self.tab_rulers.setEnabled(True)
        self.tab_rulers.triggered.connect(self.open_tab_rulers)
        about_menu.addAction(self.tab_rulers)
        
        self.about_action = QAction("About Harmonica TabViewer", self)
        self.about_action.setEnabled(True)
        self.about_action.triggered.connect(self.show_about)
        about_menu.addAction(self.about_action)

    def toggle_menus(self, switch):
        widgets = [
            self.harmonica_type,
            self.harmonica_tuning,
            self.harmonica_key,
            self.choose_part,
            self.reduce_chords,
            self.midi_button_play,
            self.open_file_menu,
            self.save_as_musicxml,
            self.print_pdf,
            self.tabs_with_bend,
            self.tabs_with_overblow,
            self.tabs_with_missing_notes,
            self.copy_tab_to_clipboard,
            self.harp_keys,
            self.tab_rulers,
            self.about_action
        ]
        for widget in widgets:
            widget.setEnabled(switch)

    def update_file_name(self):
        if self.file_path:
            self.file_name = os.path.splitext(os.path.basename(self.file_path))[0]

            if self.file_name:
                self.save_as_musicxml.setText(f"Export {self.file_name} as .musicxml")
                self.print_pdf.setText(f"Export {self.file_name} as .pdf")
                self.setWindowTitle(f"Harmonica TabViewer - {self.file_path}")
    
    def close_instances(self):
        if hasattr(self, 'sheet_viewer') and isinstance(self.sheet_viewer, SheetViewer):
            if hasattr(self.sheet_viewer, 'file_handler') and isinstance(self.sheet_viewer.file_handler, FileHandler):
                del self.sheet_viewer.file_handler
            if hasattr(self.sheet_viewer, 'score_editor') and isinstance(self.sheet_viewer.score_editor, ScoreEditor):
                if hasattr(self.sheet_viewer.score_editor, 'harps_handler') and isinstance(self.sheet_viewer.score_editor.harps_handler, TuningHandler):
                    del self.sheet_viewer.score_editor.harps_handler
                del self.sheet_viewer.score_editor
            if hasattr(self.sheet_viewer, 'svg_handler') and isinstance(self.sheet_viewer.svg_handler, SVGHandler):
                del self.sheet_viewer.svg_handler
            del self.sheet_viewer
        if hasattr(self, 'midi_player') and isinstance(self.midi_player, MidiPlayer):
            del self.midi_player

    def open_file(self):
        file_dialog = QFileDialog(self)
        self.file_path = file_dialog.getOpenFileName(self, "Open MIDI or MUSICXML File", "", "MIDI and MUSICXML files (*.mid *.midi *.musicxml)")[0]
        if self.file_path:
            try:
                self.update_file_name()
                self.toggle_menus(True)
                self.close_instances()
                self.sheet_viewer = SheetViewer(self)
                self.start_sheets(True)
                self.update_part_change()

            except Exception as e:
                print(f'Failed to load file. Reason: {e}')

    def make_temp_directory(self):
        self.temp_dir = os.path.join(tempfile.gettempdir(), "harmonica_tabviewer")
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def start_sheets(self, first_use):
        self.harmonica_key_index = self.harmonica_key.currentIndex()
        self.sheet_viewer.get_score(
            first_use, 
            self.choose_part,
        )
        self.harmonica_key_index = self.sheet_viewer.update_key_options(
            self.tabs_with_bend, 
            self.tabs_with_overblow, 
            self.tabs_with_missing_notes, 
            self.harmonica_key,
            self.harmonica_key_index,
            self.harmonica_key_options_copy
        )
        self.score_info = self.sheet_viewer.update_sheets_viewer(
            self.harmonica_key_index,
            self.reduce_chords
        )
        if self.score_info:
            self.tab_in_text = self.score_info['tab_in_text']
            self.parts_num = self.score_info['parts_num']
            self.removed_chords = self.score_info['removed_chords']
            self.removed_notes = self.score_info['removed_notes']
            self.mei_data = self.score_info['mei_data']

    def on_type_change(self):
        self.harmonica_tuning.blockSignals(True)
        self.harmonica_tuning.clear() 
        self.harmonica_key.blockSignals(True)
        self.harmonica_key.clear() 

        if self.harmonica_type.currentText() == 'Diatonic':
            tuning_options = self.harmonica_tuning_options
            key_options = self.harmonica_key_options.copy()
        elif self.harmonica_type.currentText() == 'Chromatic':
            tuning_options = ["Solo"]
            key_options = [("C", "C4")]

        for tuning in tuning_options:
            self.harmonica_tuning.addItem(tuning)

        for key, value in key_options:
            self.harmonica_key.addItem(key, value)

        self.harmonica_tuning.blockSignals(False)
        self.harmonica_key.blockSignals(False)

        self.start_sheets(False)

    def on_tuning_change(self):
        self.start_sheets(False)

    def on_key_change(self):
        self.start_sheets(False)

    def on_part_change(self):
        self.start_sheets(False)

    def update_part_change(self):
        self.choose_part.blockSignals(True)
        self.choose_part.clear()   
        self.choose_part_options = [f'{i}°' for i in range(1, self.parts_num + 1)]
        self.choose_part.addItems(self.choose_part_options)
        self.choose_part.blockSignals(False)

    def on_chord_change(self):
        self.start_sheets(False)

        if self.reduce_chords.isChecked():
            self.status_bar.showMessage(f"A total of {self.removed_notes} notes were removed from {self.removed_chords} chords", 8000)
        else:
            self.status_bar.showMessage(f"A total of {self.removed_notes} notes were restored to {self.removed_chords} chords", 8000)

        # Midi Preview with chords not implemented yet
        if self.reduce_chords.isChecked():
            self.midi_button_play.setEnabled(True)
        else:
            self.midi_button_play.setEnabled(False)

    def on_play_midi(self):
        if hasattr(self, 'midi_player') and isinstance(self.midi_player, MidiPlayer):
            self.midi_player.stop_midi()
            del self.midi_player

        self.midi_player = MidiPlayer(self)
        self.midi_player.play_midi()
        self.toggle_menus(False)
        self.midi_button_stop.setEnabled(True)

    def on_stop_midi(self):
        if hasattr(self, 'midi_player') and isinstance(self.midi_player, MidiPlayer):
            self.midi_player.stop_midi()
            del self.midi_player

    def toggle_tabs_with_bend(self):
        self.start_sheets(False)

    def toggle_tabs_with_overblow(self):
        self.start_sheets(False)

    def toggle_tabs_with_missing_notes(self):
        self.start_sheets(False)
    
    def save_file_as_musicxml(self):
        self.musicxml_path = os.path.join(self.temp_dir, f"{self.file_name}.musicxml")
        if self.musicxml_path: 
            file_dialog = QFileDialog()
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)
            file_dialog.selectFile(self.file_name)
            file_dialog.setNameFilters(["MusicXML files (*.musicxml)"])
            file_dialog.setDefaultSuffix('musicxml')
            if file_dialog.exec():
                choosed_path = file_dialog.selectedFiles()[0]

                if choosed_path:
                    with open(self.musicxml_path, 'r') as musicxml_file:
                        musicxml_content = musicxml_file.read()
                    
                    musicxml_byte_array = QByteArray(musicxml_content.encode('utf-8'))
                    with open(choosed_path, 'wb') as file:
                        file.write(musicxml_byte_array)

    def save_file_as_pdf(self):
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.selectFile(self.file_name)
        file_dialog.setNameFilters(["PDF Files (*.pdf)"])
        file_dialog.setDefaultSuffix("pdf")

        if file_dialog.exec():
            self.printer = QWebEngineView()
            svg_file_path = self.sheet_viewer.create_sheets_to_pdf()
            url = QUrl.fromLocalFile(svg_file_path)
            self.printer.load(url)

            choosed_path = file_dialog.selectedFiles()[0]
            page_layout = QPageLayout(QPageSize(QPageSize.A2), QPageLayout.Portrait, QMarginsF())
            self.printer.page().printToPdf(choosed_path, page_layout)

            self.status_bar.showMessage(f"Tablature of {self.file_name} was saved successfully.", 8000)

    def copy_to_clipboard(self):
        if self.tab_in_text:
            clipboard = QGuiApplication.instance().clipboard()
            clipboard.setText(self.tab_in_text)

            self.file_name = os.path.splitext(os.path.basename(self.file_path))[0]
            self.status_bar.showMessage(f"Tablature of {self.file_name} copied to clipboard.", 8000)

    def open_harp_keys(self):
        if self.frameview:
            harp_keys = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'charts', 'harp-keys.svg'))
            file = QUrl.fromLocalFile(harp_keys)
            self.frameview.load(file)

    def open_tab_rulers(self):
        if self.frameview:
            tab_rulers = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'charts', 'tab-rulers.svg'))
            file = QUrl.fromLocalFile(tab_rulers)
            self.frameview.load(file)

    def show_about(self):
        pass

    def closeEvent(self, event):
        try:
            self.temp_dir = os.path.join(tempfile.gettempdir(), "harmonica_tabviewer")
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f'Failed to delete temp directory {self.temp_dir}. Reason: {e}')
        event.accept()
