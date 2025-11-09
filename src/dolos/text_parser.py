"""Text parsing utilities for sentence segmentation."""

import re
from typing import List


class SentenceParser:
    """Parse text into sentences."""

    def __init__(self):
        """Initialize sentence parser."""
        # Regex pattern for sentence boundaries
        # Matches: . ! ? followed by space/end, accounting for abbreviations
        self.sentence_pattern = re.compile(
            r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s+(?=[A-Z])|(?<=\.|\?|\!)$'
        )

    def parse(self, text: str) -> List[str]:
        """Parse text into sentences.

        Args:
            text: Input text to parse

        Returns:
            List of sentences
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        if not text:
            return []

        # Split by sentence boundaries
        sentences = self.sentence_pattern.split(text)

        # Clean and filter sentences
        sentences = [s.strip() for s in sentences if s.strip()]

        # If no sentences found (no proper punctuation), return whole text as one sentence
        if not sentences:
            sentences = [text]

        return sentences

    def parse_simple(self, text: str) -> List[str]:
        """Simple sentence parsing by splitting on common punctuation.

        This is a fallback method that's more aggressive than the regex approach.

        Args:
            text: Input text to parse

        Returns:
            List of sentences
        """
        # Split on . ! ?
        sentences = re.split(r'[.!?]+', text)

        # Clean and filter
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences


def split_into_sentences(text: str, method: str = "regex") -> List[str]:
    """Convenience function to split text into sentences.

    Args:
        text: Input text
        method: Parsing method ('regex' or 'simple')

    Returns:
        List of sentences
    """
    parser = SentenceParser()

    if method == "simple":
        return parser.parse_simple(text)
    else:
        return parser.parse(text)
