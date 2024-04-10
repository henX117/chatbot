from PyPDF4 import PdfFileMerger
import os

class PDFMerger:
    def __init__(self, output_file="Final_pdf.pdf"):
        self.merger = PdfFileMerger()
        self.output_file = output_file

    def merge_pdfs(self, directory=None):
        if directory is None:
            directory = os.getcwd()

        for item in os.listdir(directory):
            if item.endswith('.pdf') and item != self.output_file:
                self.merger.append(os.path.join(directory, item))

        self.merger.write(os.path.join(directory, self.output_file))
        self.merger.close()

    def clean_up(self, directory, delete_files):
        if delete_files.lower() == 'y':
            for item in os.listdir(directory):
                if item.endswith('.pdf') and item != self.output_file:
                    os.remove(os.path.join(directory, item))
            print("Original PDF files have been deleted.")
        else:
            print("Original PDF files have been kept.")