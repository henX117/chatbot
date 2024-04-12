# pdfconverter.py
import img2pdf
import os

class PNGToPDFConverter:
    def convert(self, png_paths, output_path):
        try:
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(png_paths))
            print(f"PDF file saved successfully: {output_path}")
            return True
        except Exception as e:
            print(f"An error occurred during PNG to PDF conversion: {e}")
            return False