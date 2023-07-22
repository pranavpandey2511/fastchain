from langchain.document_loaders import PyPDFLoader
from typing import List, Union
from base_loader import BaseDataloader


class PdfDataLoader(BaseDataloader):
    def __init__(self, paths: Union[str, List]) -> None:
        """Load any pdf file from url or local path (defaults to local path).

        Args:
            path (srt): Path to the pdf file (local or url)
        """

        self.paths = paths
        if isinstance(self.paths, List):
            for path in self.paths:
                self.loader = PyPDFLoader(path)
                self.output = []

    def load_data(self) -> List:
        """
        Load pdf data and split into pages
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
            raise ValueError("No pages found in the PDF !")
