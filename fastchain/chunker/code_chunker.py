from tree_sitter import Node
import os
from enum import Enum

from fastchain.chunker.schema import Chunker


class ProgrammingLanguage(str, Enum):
    """
    Enumeration for all programming languages that are supported"""

    PYTHON = "python"
    MOJO = "mojo"
    RST = "rst"
    RUBY = "ruby"
    GO = "go"
    CPP = "cpp"
    JAVA = "java"
    JS = "js"
    TS = "ts"
    PHP = "php"
    PROTO = "proto"
    RUST = "rust"
    SCALA = "scala"
    SQL = "sql"
    KOTLIN = "kotlin"
    SWIFT = "swift"
    MARKDOWN = "markdown"
    LATEX = "latex"
    HTML = "html"
    CSHARP = "csharp"


class CodeChunker(Chunker):
    def __init__(self):
        self.parser = None
        self.language = None
        self.node = Node
