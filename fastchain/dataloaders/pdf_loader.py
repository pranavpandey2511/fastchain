from typing import List, Union, Optional, Dict
from pathlib import Path
import fitz

class PyPDFLoader:
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

    def load_and_split(self) -> List[Dict]:
        if self.include_metadata:
            self.extra_info["total_pages"] = len(self.doc)
            self.extra_info["file_path"] = str(self.file_path)
            return [{"content": page.get_text(), "extra_info": dict(self.extra_info, **{"source": f"{page.number+1}"})} for page in self.doc]
        else:
            return [{"content": page.get_text(), "extra_info": self.extra_info} for page in self.doc]

class PdfDataLoader:
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

    def load_data(self) -> List[Dict[str, Union[str, List[Dict]]]]:
        output = [{"file": file_path, "data": loader.load_and_split()} for file_path, loader in self.loaders.items()]
        self._verify_data(output)
        return output

    def _verify_data(self, data: List[Dict[str, Union[str, List[Dict]]]]) -> bool:
        if not any(item["data"] for item in data):
            raise ValueError("No pages found in the PDF files")
        return True

    @staticmethod
    def _check_dir(path: str) -> bool:
        path = Path(path)
        return path.is_dir()