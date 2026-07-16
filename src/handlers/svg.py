import os

class SVGHandler:
    def __init__(self, file_path, file_name, temp_dir):
        self.file_path = file_path
        self.file_name = file_name
        self.temp_dir = temp_dir

    def svg_stacker(self, svg_pages):

        sheets_pages = []
        for svg in svg_pages:
            sheets_pages.append(f'<div class="page">{svg}</div>')

        html_content = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ background: white; }}
                svg {{ width: 100%;}}
            </style>
        </head>
        <body>
            {'\n'.join(sheets_pages)}
        </body>
        </html>"""

        html_path = os.path.join(self.temp_dir, f"{self.file_name}.html")
        with open(html_path, 'w', encoding='utf-8') as file:
            file.write(html_content)

        return html_path
