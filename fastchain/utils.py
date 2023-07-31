import re


def preprocess_text(text: str) -> str:
    """Cleans an input string by removing unnecessary characters like newlines, tabs, etc. and making it suitable
    for further processing like tokenization, etc.

    Args:
        text (str): Input text string to be cleaned.

    Returns:
        str: Cleaned output string.
    """

    # Strip the string to remove trailing whitespaces
    text = text.strip()

    # Replace multiple newlines with a spaces:
    text = re.sub(r"\n+", " ", text)

    # Replace multiple spaces with a single space:
    text = re.sub(r"\s+", " ", text)

    # Remove all backslashes from the text:
    text = text.replace("\\", "")

    # Eliminating consecutive non-alphanumeric characters:
    # This regex identifies consecutive non-alphanumeric characters (i.e., not
    # a word character [a-zA-Z0-9_] and not a whitespace) in the string
    # and replaces each group of such characters with a single occurrence of
    # that character.
    # For example, "!!! hello !!!" would become "! hello !".
    output_text = re.sub(r"([^\w\s])\1*", r"\1", text)

    return output_text
