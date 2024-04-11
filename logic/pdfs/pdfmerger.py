from PyPDF4 import PdfFileMerger
import os

class PDFMerger:
    def __init__(self, output_file="Final_pdf.pdf"):
        self.merger = PdfFileMerger()
        self.output_file = output_file

    def merge_pdfs(self, input_dir):
        for item in os.listdir(input_dir):
            if item.endswith('pdf') and item != self.output_file:
                self.merger.append(os.path.join(input_dir, item))
        output_path = os.path.join(input_dir, self.output_file)
        self.merger.write(output_path)
        self.merger.close()
        return output_path

    def clean_up(self, directory):
        for item in os.listdir(directory):
            if item.endswith('.pdf') and item != self.output_file:
                os.remove(os.path.join(directory, item))
        print("Original PDF files have been deleted.")