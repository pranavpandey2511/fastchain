"""Text chunkers"""
import os
from typing import Callable, List, Optional

from fastchain.chunker.schema import Chunker, Chunk
from fastchain.constants import (
    DEFAULT_CHUNK_SIZE,
    MAX_CHUNK_SIZE_TOKENS,
    DEFAULT_CHUNK_OVERLAP_SIZE,
)
from fastchain.dataloaders.utils import num_tokens_from_string
import tiktoken
from pydantic import BaseModel, Field
from nltk.tokenize import sent_tokenize
import math
import re
import logging
import logging.config
from dotenv import load_dotenv

CHUNK_OVERLAP_SIZE = 200
CHUNKING_REGEX = "[^,.;。]+[,.;。]?"
PARAGRAPH_REGEX = ""
DEFUALT_PARAGRAPH_SEP = "\n\n\n"

load_dotenv()

logging.config.fileConfig(
    fname=os.environ.get("LOGGER_CONF_FILE"), disable_existing_loggers=False
)

# Get the logger specified in the file
logger = logging.getLogger(__name__)


# Write a function which takes a string text and divides it into paragraphs, the paragrpahs can be random in nature
def _split_paragraphs(text: str) -> List[str]:
    """Divide a string text into paragraphs.

    Args:
        text (str): Text to be divided

    Returns:
        List[str]: List of paragraphs
    """
    paragraphs = text.split("\n\n")
    return paragraphs


def _split_sentences(text: str):
    return sent_tokenize(text)


def _split_by_sep(text: str, separator: str = "."):
    """Split text by a separator."""
    return text.split(separator)


def _split_and_keep_separator(text: str, separator: str = "."):
    """Split text by a separator and keep the separator in the splitted strings.

    Args:
        text (str): Text to be divided
        separator (str): Separator to split the text

    Returns:
        List[str]: List of splitted strings with separator attached to the previous string
    """
    splitted_strings = re.split(f"({separator})", text)
    return [
        "".join(x) for x in zip(splitted_strings[0::2], splitted_strings[1::2])
    ]


class TextChunker(Chunker, BaseModel):
    """This class is used to chunk text using text length limits."""

    _chunk_size: int = Field(
        default=DEFAULT_CHUNK_SIZE, alias="text_chunk_size"
    )
    _chunk_overlap: int = Field(
        default=DEFAULT_CHUNK_OVERLAP_SIZE, alias="text_chunk_overlap"
    )
    _length_function: Callable = Field(
        default=len, alias="text_length_function"
    )

    @classmethod
    def class_name(cls) -> str:
        """Get class name."""
        return "TokenTextChunker"

    def create_pages(self, texts: List[str]):
        ...

    def create_chunks(self, text: str):
        paragraphs = _split_paragraphs(text)


class TokenTextChunker(Chunker, BaseModel):
    _chunk_size: int = Field(
        default=DEFAULT_CHUNK_SIZE, alias="token_chunk_size"
    )
    _chunk_overlap: int = Field(
        default=DEFAULT_CHUNK_OVERLAP_SIZE, alias="token_chunk_overlap"
    )
    _length_function: Callable = Field(
        default=len, alias="text_length_function"
    )

    def create_chunks(self, text: str):
        paragraphs = _split_paragraphs(text)

        """Initialize with parameters."""
        if self._chunk_overlap > self._chunk_size:
            raise ValueError(
                f"Got a larger chunk overlap ({self.chunk_overlap}) than chunk size "
                f"({self.chunk_size}), should be smaller."
            )

    @classmethod
    def class_name(cls) -> str:
        """Get class name."""
        return "TokenTextChunker"

    def chunk_by_token_limit(
        self, text, token_limit, *, overlap=20, model="gpt-3.5-turbo"
    ) -> List[str]:
        # Count number of tokens
        num_tokens = num_tokens_from_string(text, model)

        # Check if the text fits within the token limit
        if num_tokens <= token_limit:
            return [text]

        # Calculate the number of chunks needed
        num_chunks = (num_tokens - overlap) // (token_limit - overlap) + 1

        # Calculate the target tokens per chunk
        tokens_per_chunk = math.ceil(num_tokens / num_chunks)

        # Initialize variables
        text_chunks = []
        current_chunk = ""
        current_chunk_tokens = 0

        # Split the text into words
        all_words = text.split()

        # Iterate over the words
        for word in all_words:
            # Count the tokens in the current word
            word_tokens = num_tokens_from_string(word, model)

            # Check if adding the current word would exceed the token limit
            if current_chunk_tokens + word_tokens <= tokens_per_chunk:
                # Add the word to the current chunk
                current_chunk += " " + word
                current_chunk_tokens += word_tokens
            else:
                # Start a new chunk
                text_chunks.append(current_chunk.strip())
                current_chunk = word
                current_chunk_tokens = word_tokens

                # Add overlap
                if len(text_chunks) > 0 and overlap > 0:
                    overlap_text = " ".join(text_chunks[-1].split()[-overlap:])
                    current_chunk = overlap_text + " " + current_chunk
                    current_chunk_tokens += num_tokens_from_string(
                        overlap_text, model
                    )

        # Add the last chunk
        if current_chunk:
            text_chunks.append(current_chunk.strip())

        return text_chunks

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


class TokenChunker(Chunker, BaseModel):
    """This class is used to chunk text using token limits."""
