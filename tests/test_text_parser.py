"""Tests for text parsing."""

import pytest
from dolos.text_parser import SentenceParser, split_into_sentences


class TestSentenceParser:
    """Test sentence parsing functionality."""

    def test_simple_sentences(self):
        """Test parsing simple sentences."""
        parser = SentenceParser()
        text = "This is sentence one. This is sentence two. This is sentence three."
        sentences = parser.parse(text)

        assert len(sentences) == 3
        assert "sentence one" in sentences[0]
        assert "sentence two" in sentences[1]
        assert "sentence three" in sentences[2]

    def test_question_marks(self):
        """Test parsing with question marks."""
        parser = SentenceParser()
        text = "What is this? This is a test. How does it work?"
        sentences = parser.parse(text)

        assert len(sentences) >= 2

    def test_exclamation_marks(self):
        """Test parsing with exclamation marks."""
        parser = SentenceParser()
        text = "Hello! This is exciting! Amazing stuff!"
        sentences = parser.parse(text)

        assert len(sentences) >= 2

    def test_empty_text(self):
        """Test parsing empty text."""
        parser = SentenceParser()
        sentences = parser.parse("")

        assert len(sentences) == 0

    def test_single_sentence(self):
        """Test parsing single sentence."""
        parser = SentenceParser()
        text = "This is a single sentence."
        sentences = parser.parse(text)

        assert len(sentences) == 1
        assert "single sentence" in sentences[0]

    def test_no_punctuation(self):
        """Test parsing text without sentence-ending punctuation."""
        parser = SentenceParser()
        text = "This has no ending punctuation"
        sentences = parser.parse(text)

        assert len(sentences) == 1
        assert text in sentences[0]

    def test_split_into_sentences_function(self):
        """Test convenience function."""
        text = "First sentence. Second sentence."
        sentences = split_into_sentences(text)

        assert len(sentences) >= 1
