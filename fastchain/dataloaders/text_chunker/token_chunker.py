import tiktoken
import math
from fastchain.dataloaders.utils import num_tokens_from_string


def chunk_text_by_token_limit(
    text, token_limit, *, overlap=20, model="gpt-3.5-turbo"
):
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


def tokenize(text, model="gpt-3.5-turbo"):
    pass
