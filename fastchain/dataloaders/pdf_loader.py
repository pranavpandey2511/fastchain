from typing import List, Union, Optional, Dict
from pathlib import Path
import fitz
from unidecode import unidecode
from .base import Dataloader

class PyPDFLoader(Dataloader):
    def __init__(self, file_path: Union[str, Path], include_metadata: bool = True, extra_info: Optional[Dict] = None):
        if not isinstance(file_path, (str, Path)):
            raise TypeError("file_path must be a string or Path.")

        self.file_path = file_path
        self.include_metadata = include_metadata
        self.extra_info = extra_info if extra_info else {}

        try:
            self.doc = fitz.open(str(file_path))
        except Exception as e:
            raise Exception(f"Failed to open {file_path}: {str(e)}")

    def load_and_split(self) -> Dict:
        pages_content = []
        if self.include_metadata:
            self.extra_info["total_pages"] = len(self.doc)
            self.extra_info["file_path"] = str(self.file_path)
        for page_number, page in enumerate(self.doc):
            page_content = []
            output = page.get_text("blocks")
            previous_block_id = 0
            for block in output:
                if block[6] == 0:  # We only take the text
                    block_decoded = unidecode(block[4])
                    content_block = {"content": block_decoded}
                    if self.include_metadata:
                        content_block["extra_info"] = dict(self.extra_info, **{"source": f"{page_number+1}", "block_no": block[5]})
                    if previous_block_id != block[5]:
                        content_block["new_block"] = True
                        previous_block_id = block[5]
                    page_content.append(content_block)
            pages_content.append(page_content)
        return {str(self.file_path): pages_content}



class PdfDataLoader(Dataloader):
    def __init__(
        self,
        path: Union[str, List[str], Path, List[Path]],
        recursive: bool = True,
        include_metadata: bool = True,
        *,
        exclude: List[str] = [],
    ) -> None:
        self.path = path if isinstance(path, list) else [path]
        self.recursive = recursive
        self.include_metadata = include_metadata
        self.exclude = exclude

        pdf_files = self._get_pdf_files()
        self.loaders = {str(file_path): PyPDFLoader(file_path, include_metadata) for file_path in pdf_files}

    def _get_pdf_files(self) -> List[Union[str, Path]]:
        pdf_files = []
        for file_path in self.path:
            path = Path(file_path)
            if self._check_dir(file_path):
                if self.recursive:
                    pdf_files.extend([str(p) for p in path.rglob("*.pdf")])
                else:
                    pdf_files.extend([str(p) for p in path.glob("*.pdf")])
            elif path.is_file() and path.suffix == ".pdf":
                pdf_files.append(str(path))

        return [file for file in pdf_files if file not in self.exclude]

    def load_data(self) -> Dict:
        output = {}
        for file_path, loader in self.loaders.items():
            output.update(loader.load_and_split())
        self._verify_data(output)
        return output


    def _verify_data(self, data: List[Dict]) -> bool:
        if not any(data):
            raise ValueError("No pages found in the PDF file")
        return True

    @staticmethod
    def _check_dir(path: str) -> bool:
        path = Path(path)
        return path.is_dir()