# A helpful rule of thumb is that one token generally corresponds to ~4 characters
# of text for common English text. This translates to roughly ¾ of a word (so 100 tokens ~= 75 words).

#### TextChunker
DEFAULT_CHUNK_SIZE = 1600
DEFAULT_CHUNK_OVERLAP_SIZE = 160

#### TokenChunker
DEFAULT_TOKEN_CHUNK_SIZE = 512
DEFAULT_TOKEN_CHUNK_OVERLAP_SIZE = 50
MAX_TOKEN_CHUNK_SIZE = 512

MAX_CHUNK_SIZE_TOKENS = 512

DEFUALT_PARAGRAPH_SEP = "\n\n\n"

#### CodeChunker
IGNORE_EXTENSIONS = [
    ".min.js",
    ".min.js.map",
    ".min.css",
    ".min.css.map",
    ".tfstate",
    ".tfstate.backup",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".tiff",
    ".ico",
    ".mp3",
    ".wav",
    ".wma",
    ".ogg",
    ".flac",
    ".mp4",
    ".avi",
    ".mkv",
    ".mov",
    ".wmv",
    ".m4a",
    ".m4v",
    ".3gp",
    ".3g2",
    ".rm",
    ".swf",
    ".flv",
    ".iso",
    ".bin",
    ".tar",
    ".zip",
    ".7z",
    ".gz",
    ".rar",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".svg",
    ".parquet",
    ".pyc",
    ".pub",
    ".pem",
]
