"""Utility function tests."""

from bambara_normalizer import (
    analyze_text,
    get_base_char,
    get_tone,
    has_tone_marks,
    is_bambara_char,
    is_bambara_special_char,
    remove_tones,
    validate_bambara_text,
)


class TestCharacterUtilities:
    def test_is_bambara_char(self):
        assert is_bambara_char("a") is True
        assert is_bambara_char("ɛ") is True
        assert is_bambara_char("ŋ") is True
        assert is_bambara_char("q") is False

    def test_is_bambara_special_char(self):
        assert is_bambara_special_char("ɛ") is True
        assert is_bambara_special_char("ɔ") is True
        assert is_bambara_special_char("ɲ") is True
        assert is_bambara_special_char("ŋ") is True
        assert is_bambara_special_char("a") is False

    def test_get_base_char(self):
        assert get_base_char("á") == "a"
        assert get_base_char("ɛ́") == "ɛ"
        assert get_base_char("a") == "a"


class TestToneUtilities:
    def test_get_tone_high(self):
        assert get_tone("á") == "high"

    def test_get_tone_low(self):
        assert get_tone("à") == "low"

    def test_get_tone_none(self):
        assert get_tone("a") is None

    def test_has_tone_marks_true(self):
        assert has_tone_marks("fɔ́lɔ̀") is True

    def test_has_tone_marks_false(self):
        assert has_tone_marks("fɔlɔ") is False

    def test_remove_tones(self):
        assert remove_tones("fɔ́lɔ̀") == "fɔlɔ"


class TestTextValidation:
    def test_validate_valid_text(self):
        is_valid, issues = validate_bambara_text("bɛna")
        assert is_valid is True

    def test_validate_invalid_text(self):
        is_valid, issues = validate_bambara_text("nyama")
        assert is_valid is False
        assert len(issues) > 0


class TestTextAnalysis:
    def test_analyze_text(self):
        analysis = analyze_text("Ń b'à fɔ́")
        assert "word_count" in analysis
        assert "vowel_count" in analysis
        assert "contractions_found" in analysis
        assert any("b'" in c for c in analysis["contractions_found"])
