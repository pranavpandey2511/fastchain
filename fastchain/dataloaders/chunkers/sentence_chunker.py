"""Sentence splitter."""
from dataclasses import dataclass
from typing import Callable, List, Optional
from nltk.tokenize import sent_tokenize
from fastchain.dataloaders.chunkers.schema import Chunker
from schema import Chunk
from llama_index.bridge.pydantic import Field, PrivateAttr
from fastchain.constants import DEFAULT_CHUNK_SIZE, MAX_CHUNK_SIZE_TOKENS
from pydantic import BaseModel, Field
import logging
CHUNK_OVERLAP_SIZE = 200
CHUNKING_REGEX = "[^,.;。]+[,.;。]?"
PARAGRAPH_REGEX = ""
DEFUALT_PARAGRAPH_SEP = "\n\n\n"


def _split_paragraphs(text: str):
    text = text.strip("\n")


class TextChunker(Chunker, BaseModel):
    _chunk_size: int = Field(default=config.DEFAULT_CHUNK_SIZE
        alias="text_chunk_size",
    )
    _chunk_overlap: int = chunk_overlap
    _length_function = length_function
    _keep_separator = keep_separator
    _strip_whitespace = strip_whitespace

    def __init__(self):
        ...

    def create_chunks(self, text):
        ...


class SentenceSplitter:
    """Split the text into complete sentances whenever possible."""

    chunk_size: int = Field(
        default=DEFAULT_CHUNK_SIZE,
        description="The token chunk size for each chunk.",
    )
    chunk_overlap: int = Field(
        default=CHUNK_OVERLAP_SIZE,
        description="The token overlap of each chunk when splitting.",
    )
    separator: str = Field(
        default=" ", description="Default separator for splitting into words"
    )
    paragraph_separator: str = Field(
        default=DEFUALT_PARAGRAPH_SEP,
        description="Separator between paragraphs.",
    )
    secondary_chunking_regex: str = Field(
        default=CHUNKING_REGEX,
        description="Backup regex for splitting into sentences.",
    )
    chunking_tokenizer_fn: Callable[[str], List[str]] = Field(
        exclude=True,
        description=(
            "Function to split text into sentences. "
            "Defaults to `nltk.sent_tokenize`."
        ),
    )
    callback_manager: CallbackManager = Field(
        default_factory=CallbackManager, exclude=True
    )
    tokenizer: Callable = Field(
        default_factory=globals_helper.tokenizer,  # type: ignore
        description="Tokenizer for splitting words into tokens.",
        exclude=True,
    )

    _split_fns: List[Callable] = PrivateAttr()
    _sub_sentence_split_fns: List[Callable] = PrivateAttr()

    def __init__(
        self,
        separator: str = " ",
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = SENTENCE_CHUNK_OVERLAP,
        tokenizer: Optional[Callable] = None,
        paragraph_separator: str = DEFUALT_PARAGRAPH_SEP,
        chunking_tokenizer_fn: Optional[Callable[[str], List[str]]] = None,
        secondary_chunking_regex: str = CHUNKING_REGEX,
        callback_manager: Optional[CallbackManager] = None,
    ):
        """Initialize with parameters."""
        if chunk_overlap > chunk_size:
            raise ValueError(
                f"Got a larger chunk overlap ({chunk_overlap}) than chunk size "
                f"({chunk_size}), should be smaller."
            )

        callback_manager = callback_manager or CallbackManager([])
        chunking_tokenizer_fn = (
            chunking_tokenizer_fn or split_by_sentence_tokenizer()
        )
        tokenizer = tokenizer or globals_helper.tokenizer

        self._split_fns = [
            split_by_sep(paragraph_separator),
            chunking_tokenizer_fn,
        ]

        self._sub_sentence_split_fns = [
            split_by_regex(secondary_chunking_regex),
            split_by_sep(separator),
            split_by_char(),
        ]

        super().__init__(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            chunking_tokenizer_fn=chunking_tokenizer_fn,
            secondary_chunking_regex=secondary_chunking_regex,
            separator=separator,
            paragraph_separator=paragraph_separator,
            callback_manager=callback_manager,
            tokenizer=tokenizer,
        )

    @classmethod
    def class_name(cls) -> str:
        """Get class name."""
        return "SentenceSplitter"

    def split_text_metadata_aware(
        self, text: str, metadata_str: str
    ) -> List[str]:
        metadata_len = len(self.tokenizer(metadata_str))
        effective_chunk_size = self.chunk_size - metadata_len
        if effective_chunk_size <= 0:
            raise ValueError(
                f"Metadata length ({metadata_len}) is longer than chunk size "
                f"({self.chunk_size}). Consider increasing the chunk size or "
                "decreasing the size of your metadata to avoid this."
            )
        elif effective_chunk_size < 50:
            print(
                f"Metadata length ({metadata_len}) is close to chunk size "
                f"({self.chunk_size}). Resulting chunks are less than 50 tokens. "
                "Consider increasing the chunk size or decreasing the size of "
                "your metadata to avoid this.",
                flush=True,
            )

        return self._split_text(text, chunk_size=effective_chunk_size)

    def split_text(self, text: str) -> List[str]:
        return self._split_text(text, chunk_size=self.chunk_size)

    def _generate_chunks(
        self, text: str, chunk_size: int = DEFAULT_CHUNK_SIZE
    ) -> List[Chunk]:
        ...

    def _split_into_words(self, text: str) -> List[str]:
        if not text:
            return []

        words = sent_tokenize(text)

        return words

    def _merge_into_chunks(
        self,
        words: List[str],
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap_size: int = CHUNK_OVERLAP_SIZE,
    ):
        pass

    def _split_text(self, text: str, chunk_size: int) -> List[str]:
        """
        _Split incoming text and return chunks with overlap size.

        Has a preference for complete sentences, phrases, and minimal overlap.
        """
        if text == "":
            return []

        with self.callback_manager.event(
            CBEventType.CHUNKING, payload={EventPayload.CHUNKS: [text]}
        ) as event:
            splits = self._split(text, chunk_size)
            chunks = self._merge(splits, chunk_size)

            event.on_end(payload={EventPayload.CHUNKS: chunks})

        return chunks

    def _split(self, text: str, chunk_size: int) -> List[_Split]:
        """Break text into splits that are smaller than chunk size.

        The order of splitting is:
        1. split by paragraph separator
        2. split by chunking tokenizer (default is nltk sentence tokenizer)
        3. split by second chunking regex (default is "[^,\.;]+[,\.;]?")
        4. split by default separator (" ")

        """
        if len(self.tokenizer(text)) <= chunk_size:
            return [Chunk(text, is_sentence=True)]

        for split_fn in self._split_fns:
            splits = split_fn(text)
            if len(splits) > 1:
                break

        if len(splits) > 1:
            is_sentence = True
        else:
            for split_fn in self._sub_sentence_split_fns:
                splits = split_fn(text)
                if len(splits) > 1:
                    break
            is_sentence = False

        new_splits = []
        for split in splits:
            split_len = len(self.tokenizer(split))
            if split_len <= chunk_size:
                new_splits.append(_Split(split, is_sentence=is_sentence))
            else:
                ns = self._split(split, chunk_size=chunk_size)
                if len(ns) == 0:
                    print("0 length split")
                # recursively split
                new_splits.extend(ns)
        return new_splits

    def _merge(self, splits: List[_Split], chunk_size: int) -> List[str]:
        """Merge splits into chunks."""
        chunks: List[str] = []
        cur_chunk: List[str] = []
        cur_chunk_len = 0
        while len(splits) > 0:
            cur_split = splits[0]
            cur_split_len = len(self.tokenizer(cur_split.text))
            if cur_split_len > chunk_size:
                raise ValueError("Single token exceed chunk size")
            if (
                cur_chunk_len + cur_split_len > chunk_size
                and len(cur_chunk) > 0
            ):
                # if adding split to current chunk exceed chunk size: close out chunk
                chunks.append("".join(cur_chunk).strip())
                cur_chunk = []
                cur_chunk_len = 0
            else:
                if (
                    cur_split.is_sentence
                    or cur_chunk_len + cur_split_len
                    < chunk_size - self.chunk_overlap
                    or len(cur_chunk) == 0
                ):
                    # add split to chunk
                    cur_chunk_len += cur_split_len
                    cur_chunk.append(cur_split.text)
                    splits.pop(0)
                else:
                    # close out chunk
                    chunks.append("".join(cur_chunk).strip())
                    cur_chunk = []
                    cur_chunk_len = 0

        # handle the last chunk
        chunk = "".join(cur_chunk).strip()
        if chunk:
            chunks.append(chunk)

        # run postprocessing to remove blank spaces
        chunks = self._postprocess_chunks(chunks)

        return chunks

    def _postprocess_chunks(self, chunks: List[str]) -> List[str]:
        """Post-process chunks."""
        new_chunks = []
        for doc in chunks:
            if doc.replace(" ", "") == "":
                continue
            new_chunks.append(doc)
        return new_chunks
