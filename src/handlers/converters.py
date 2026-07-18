import os
import verovio
from music21 import converter
from music21.musicxml import m21ToXml

class FileHandler:
    def __init__(self, file_path, file_name, temp_dir): 
        self.file_path = file_path
        self.file_name = file_name
        self.temp_dir = temp_dir

        self.toolkit = verovio.toolkit()

        self.toolkit.setOptions({
            "footer": "none", # Turn off verovio watermark
            #"header": "none"
        })

    def midi_to_musicxml(self, part_pos):
        score = converter.parse(self.file_path)
        part_num = len(score.parts)
        piece = score.parts[part_pos - 1]

        return piece, part_num

    def musicxml_to_mei(self, piece):

        exporter = m21ToXml.GeneralObjectExporter()
        xml_bytes = exporter.parse(piece)
        xml_string = xml_bytes.decode('utf-8')

        self.toolkit.loadData(xml_string)
        mei_data = self.toolkit.getMEI()

        return mei_data

    #def mei_to_svg_files(self, mei_data):
    #    self.toolkit.loadData(mei_data)
    #    page_num = self.toolkit.getPageCount()
    #    svg_files = []
    #    
    #    for page in range(1, page_num + 1):
    #        svg_file_path = os.path.join(self.temp_dir, f"{self.file_name}_page{page}.svg")
    #        self.toolkit.renderToSVGFile(svg_file_path, page)
    #        svg_files.append(svg_file_path)
    #
    #    return svg_files
    
    def mei_to_midi(self, mei_data):
        midi_path = os.path.join(self.temp_dir, f"{self.file_name}.mid")

        self.toolkit.loadData(mei_data)
        self.toolkit.renderToMIDIFile(midi_path)  # Rare occurrence: Some data can crash the app after running this

        return midi_path

    # Get data instead of write svg files
    def musicxml_to_svg(self, piece):
        
        mei_data = self.musicxml_to_mei(piece)
        
        self.toolkit.loadData(mei_data)
        page_num = self.toolkit.getPageCount()
        svg_sheet = []
        
        for page in range(1, page_num + 1):
            svg_page = self.toolkit.renderToSVG(page)
            svg_sheet.append(svg_page)

        return svg_sheet, mei_data
