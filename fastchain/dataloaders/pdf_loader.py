from langchain.document_loaders import PyPDFLoader, PyMuPDFLoader
from typing import List, Union
from base_loader import BaseDataloader
import os
from pathlib import Path


class PdfDataLoader(BaseDataloader):
    def __init__(
        self,
        path: Union[str, List],
        recursive: bool = True,
        *,
        exclude: List[str] = [],
    ) -> None:
        """Load any pdf file from url or local path (defaults to local path).

        Args:
            path (srt): Path to the pdf file (local or url)
        """

        self.path = path
        if isinstance(self.paths, List):
            for file_path in self.path:
                if file_path.endswith(".pdf"):
                    self.loader = PyPDFLoader(file_path)
                    self.output = []

    def _create_loaders(self):
        """Create separate loaders for each file. If the path is a directory, create a loader for each file in the directory. If option is set to be recursive, do it recursively for each pdf file in every folder, make sure that paths that are excluded (directory or filepath) should not be loded."""
        if self._check_dir(self.path):
            if self.recursive:
                for root, dirs, files in os.walk(self.path):
                    for file in files:
                        if file.endswith(".pdf"):
                            if file not in self.exclude:
                                self.loader = PyPDFLoader(file)
                                self.output = []
            else:
                for file in os.listdir(self.path):
                    if file.endswith(".pdf"):
                        if file not in self.exclude:
                            self.loader = PyPDFLoader(file)
                            self.output = []

    def load_data(self) -> List:
        """
        Load pdf file and split it into pages and documents
        """
        self.data = self.loader.load_and_split()
        for page in self.data:
            content = page.page_content
            content = clean_string(content)
            meta_data = page.metadata
            meta_data["url"] = url
            output.append(
                {
                    "content": content,
                    "meta_data": meta_data,
                }
            )
        return output

    def _verify_data(self) -> bool:
        """Verify data consistency

        Raises:
            ValueError: Raise Value Error if data is inconsistent

        Returns:
            Boolean: Returns True if data is consistent
        """

        if not len(self.data):
            raise ValueError("No pages found in the PDF file")

    @staticmethod
    def _check_dir(path: str) -> bool:
        """Given the path check if the path is a directory or not using pathlib

        Args:
            path (str): path to the directory/file
        """
        path = Path(path)
        if path.is_dir():
            return True
        else:
            return False


def _pymupdf_loader():
    # The import name for this library is fitz
    import fitz

    # Create a document object
    doc = fitz.open("file.pdf")  # or fitz.Document(filename)

    # Extract the number of pages (int)
    print(doc.page_count)

    # the metadata (dict) e.g., the author,...
    print(doc.metadata)

    # Get the page by their index
    page = doc.load_page(0)
    # or page = doc[0]

    # read a Page
    text = page.get_text()
    print(text)

    # Render and save the page as an image
    pix = page.get_pixmap()
    pix.save(f"page-{page.number}.png")

    # get all links on a page
    links = page.get_links()
    print(links)

    # Render and save all the pages as images
    for i in range(doc.page_count):
        page = doc.load_page(i)
        pix = page.get_pixmap()
        pix.save("page-%i.png" % page.number)

    # get the links on all pages
    for i in range(doc.page_count):
        page = doc.load_page(i)
        link = page.get_links()
        print(link)
