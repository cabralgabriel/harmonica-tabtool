import os
import shutil
import svg_stack as ss
from bs4 import BeautifulSoup

class SVGHandler:
    def __init__(self, source):
        self.file_path = source.file_path
        self.file_name = source.file_name
        self.temp_dir = source.temp_dir

    def get_last_height_value(self, svg_string):
        soup = BeautifulSoup(svg_string, 'xml')
        verses = soup.find_all('g', class_='verse')
        if verses:
            last_verse = verses[-1]
            last_syl = last_verse.find('g', class_='syl')
            if last_syl:
                text = last_syl.find('text')
                if text and 'y' in text.attrs:
                    return int(text['y']) + 600
        return 2970 

    def adjust_height(self, svg_string, height_value):
        soup = BeautifulSoup(svg_string, 'xml')
        svg_tag = soup.find('svg')
        if svg_tag and 'height' in svg_tag.attrs:
            new_height = str(height_value // 10) + 'px'
            svg_tag['height'] = new_height
        return str(soup)

    def calculate_total_height(self, svgs_files_path):
        return sum(self.get_last_height_value(self.read_svg(file_path)) for file_path in svgs_files_path)
    
    def read_svg(self, file_path):
        with open(file_path, 'r') as file:
            return file.read()

    def write_svg(self, file_path, svg_string):
        with open(file_path, 'w') as file:
            file.write(svg_string)

    def prepare_and_clean_svg(self, svg_string, index, height):
        svg_string = svg_string.replace('viewBox="0 0 21000 29700"', f'viewBox="0 0 21000 {height}"')
        if index != 0:
            svg_string = svg_string.replace('<text font-size="0px">', '<text font-size="0px" transform="scale(100, 100)">')
        svg_string = svg_string.replace('transform="translate(7750, 28099) scale(10.000000, 10.000000)"', 'transform="translate(7750, 28099) scale(0, 0)"')
        return svg_string

    def backup_svg_files(self, svgs_files_path, backup_dir):
        os.makedirs(backup_dir, exist_ok=True)
        for file_path in svgs_files_path:
            shutil.copyfile(file_path, os.path.join(backup_dir, os.path.basename(file_path)))

    def restore_svg_files(self, svgs_files_path, backup_dir):
        for file_path in svgs_files_path:
            shutil.copyfile(os.path.join(backup_dir, os.path.basename(file_path)), file_path)
        shutil.rmtree(backup_dir)

    def create_svg_document(self, svgs_files_path, total_height, output_file_name, adjust_heights=True):
        doc = ss.Document()
        layout = ss.VBoxLayout()
        temp_files = []

        for index, file_path in enumerate(svgs_files_path):
            svg_string = self.read_svg(file_path)
            svg_string = self.prepare_and_clean_svg(svg_string, index, total_height)

            if adjust_heights:
                last_syl_y = self.get_last_height_value(svg_string)
                svg_string = self.adjust_height(svg_string, last_syl_y)

            temp_file_path = os.path.join(self.temp_dir, os.path.basename(file_path))
            self.write_svg(temp_file_path, svg_string)
            layout.addSVG(temp_file_path, alignment=ss.AlignCenter)
            temp_files.append(temp_file_path)

        doc.setLayout(layout)
        svg_file_path = os.path.join(self.temp_dir, f"{output_file_name}.svg")
        doc.save(svg_file_path)

        return svg_file_path

    def svg_stacker(self, svgs_files_path):
        backup_dir = os.path.join(self.temp_dir, 'backup')
        self.backup_svg_files(svgs_files_path, backup_dir)

        total_height = self.calculate_total_height(svgs_files_path)
        svg_file_path = self.create_svg_document(svgs_files_path, total_height, self.file_name)

        self.restore_svg_files(svgs_files_path, backup_dir)

        return svg_file_path

    def svg_stacker_to_pdfprint(self, svgs_files_path):
        num_pags = len(svgs_files_path)
        tamanho_doc = num_pags * 2970 * 10

        return self.create_svg_document(svgs_files_path, tamanho_doc, f"{self.file_name}_to_pdfprint", adjust_heights=False)