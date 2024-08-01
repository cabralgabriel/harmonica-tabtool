import os
import verovio
from music21 import converter

class FileHandler:
    def __init__(self, source):
        self.file_path = source.file_path
        self.file_name = source.file_name
        self.temp_dir = source.temp_dir

        self.toolkit = verovio.toolkit()

    def midi_to_musicxml(self, part_pos):
        score = converter.parse(self.file_path)
        part_num = len(score.parts)
        piece = score.parts[part_pos - 1]

        return piece, part_num

    def musicxml_to_mei(self, musicxml_path):
        self.toolkit.loadFile(musicxml_path)
        mei_data = self.toolkit.getMEI()

        return mei_data

    def mei_to_svg(self, mei_data):
        self.toolkit.loadData(mei_data)
        page_num = self.toolkit.getPageCount()
        svg_files = []
        
        for page in range(1, page_num + 1):
            svg_file_path = os.path.join(self.temp_dir, f"{self.file_name}_page{page}.svg")
            self.toolkit.renderToSVGFile(svg_file_path, page)
            svg_files.append(svg_file_path)

        return svg_files
    
    #def mei_to_svg_data(self, mei_data):
    #    self.toolkit.loadData(mei_data)
    #    page_num = self.toolkit.getPageCount()
    #    svg_sheet = []
    #    
    #    for page in range(1, page_num + 1):
    #        svg_page = self.toolkit.renderToSVG(page)
    #        svg_sheet.append(svg_page)
    #
    #    return svg_sheet
    
    def mei_to_midi(self, mei_data):
        midi_path = os.path.join(self.temp_dir, f"{self.file_name}.mid")

        self.toolkit.loadData(mei_data)
        self.toolkit.renderToMIDIFile(midi_path)  # Rare occurrence: Some data can crash the app after running this

        return midi_path

    def musicxml_to_svg(self, piece):
        musicxml_path = os.path.join(self.temp_dir, f"{self.file_name}.musicxml")
        piece.write("musicxml", fp=musicxml_path)

        mei_data = self.musicxml_to_mei(musicxml_path)
        svg_files = self.mei_to_svg(mei_data)

        return svg_files, mei_data
