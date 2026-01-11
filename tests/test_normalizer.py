"""Core normalizer tests."""

import unicodedata

import pytest

from bambara_normalizer import (
    BambaraNormalizer,
    BambaraNormalizerConfig,
    normalize,
)


class TestBambaraNormalizer:
    def test_basic_normalization(self):
        normalizer = BambaraNormalizer()
        assert normalizer("I ni ce") == "i ni ce"

    def test_contraction_expansion_ba(self):
        normalizer = BambaraNormalizer()
        assert normalizer("An b'a fɔ Ala ni ce.") == "an bɛ a fɔ ala ni ce"
        assert normalizer("b'a") == "bɛ a"

    def test_contraction_expansion_ta(self):
        normalizer = BambaraNormalizer()
        assert normalizer("n t'a don") == "n tɛ a don"

    def test_contraction_expansion_ya(self):
        normalizer = BambaraNormalizer()
        assert normalizer("A y'a fɔ") == "a ye a fɔ"

    def test_contraction_expansion_na(self):
        normalizer = BambaraNormalizer()
        result = normalizer("i n'i ce")
        assert "ni" in result

    def test_contraction_expansion_ka_default(self):
        normalizer = BambaraNormalizer()
        result = normalizer("k'a dun")
        assert "ka" in result

    def test_multiple_contractions(self):
        normalizer = BambaraNormalizer()
        result = normalizer("Ń b'i fɛ, n t'a don")
        assert "bɛ" in result
        assert "tɛ" in result

    def test_legacy_orthography_vowels(self):
        normalizer = BambaraNormalizer()
        assert "ɛ" in normalizer("bèlè")
        assert "ɔ" in normalizer("dòn")

    def test_legacy_orthography_digraphs(self):
        normalizer = BambaraNormalizer()
        assert "ɲ" in normalizer("nyama")
        assert "ŋ" in normalizer("bango")

    def test_senegalese_variant(self):
        normalizer = BambaraNormalizer()
        assert "ɲ" in normalizer("ñama")

    def test_apostrophe_normalization(self):
        normalizer = BambaraNormalizer()
        result1 = normalizer("b'a")
        result2 = normalizer("b'a")
        result3 = normalizer("bʼa")
        assert result1 == result2 == result3

    def test_punctuation_removal(self):
        normalizer = BambaraNormalizer()
        result = normalizer("Bɔ! Ka Taa?")
        assert "!" not in result
        assert "?" not in result

    def test_whitespace_normalization(self):
        normalizer = BambaraNormalizer()
        assert normalizer("a   b\t\nc") == "a b c"

    def test_case_normalization(self):
        normalizer = BambaraNormalizer()
        assert normalizer("ƐƆƝ") == "ɛɔɲ"

    def test_preserve_tones_config(self):
        config = BambaraNormalizerConfig.preserving_tones()
        normalizer = BambaraNormalizer(config)
        result = normalizer("fɔ́lɔ̀")
        assert "́" in unicodedata.normalize("NFD", result) or "̀" in unicodedata.normalize(
            "NFD", result
        )

    def test_remove_tones_config(self):
        config = BambaraNormalizerConfig.for_wer_evaluation()
        normalizer = BambaraNormalizer(config)
        result = normalizer("fɔ́lɔ̀")
        decomposed = unicodedata.normalize("NFD", result)
        assert "\u0301" not in decomposed
        assert "\u0300" not in decomposed

    def test_number_expansion(self):
        config = BambaraNormalizerConfig.for_wer_evaluation()
        normalizer = BambaraNormalizer(config)
        assert "kelen" in normalizer("1")
        assert "fila" in normalizer("2")
        assert "tan" in normalizer("10")

    def test_empty_string(self):
        normalizer = BambaraNormalizer()
        assert normalizer("") == ""

    def test_unicode_nfc_normalization(self):
        normalizer = BambaraNormalizer()
        decomposed = "e\u0301"
        result = normalizer(decomposed)
        assert result == unicodedata.normalize("NFC", result)


class TestConvenienceFunction:
    def test_normalize_function(self):
        result = normalize("B'a fɔ́!")
        assert "bɛ" in result
        assert "a" in result
        assert "fɔ" in result

    def test_normalize_with_preset(self):
        result = normalize("B'a fɔ́!", preset="wer")
        assert isinstance(result, str)

    def test_normalize_with_kwargs(self):
        result = normalize("B'a fɔ́!", preset="standard", preserve_tones=True)
        decomposed = unicodedata.normalize("NFD", result)
        assert "\u0301" in decomposed or "\u0300" in decomposed


class TestRealWorldExamples:
    def test_example_sentence_1(self):
        normalizer = BambaraNormalizer()
        result = normalizer("Ń b'à fɛ̀")
        assert "bɛ" in result
        assert "fɛ" in result

    def test_example_sentence_2(self):
        normalizer = BambaraNormalizer()
        result = normalizer("n t'a lon")
        assert "tɛ" in result

    def test_example_sentence_3(self):
        normalizer = BambaraNormalizer()
        result = normalizer("A y'à fɔ́")
        assert "ye" in result

    def test_reported_speech_ko(self):
        normalizer = BambaraNormalizer()
        result = normalizer("A fɔ k'an ka ta so")
        assert "ko an ka" in result

    @pytest.mark.skip(reason="French loanword handling disabled")
    def test_code_switching_french(self):
        config = BambaraNormalizerConfig()
        config.handle_french_loanwords = True
        normalizer = BambaraNormalizer(config)
        result = normalizer("télé")
        assert "tele" in result


class TestEdgeCases:
    def test_only_punctuation(self):
        normalizer = BambaraNormalizer()
        assert normalizer("!!!???") == ""

    def test_only_whitespace(self):
        normalizer = BambaraNormalizer()
        assert normalizer("   \t\n   ") == ""

    def test_mixed_scripts(self):
        normalizer = BambaraNormalizer()
        result = normalizer("bɛna 你好")
        assert "bɛna" in result

    def test_very_long_text(self):
        normalizer = BambaraNormalizer()
        long_text = "bɛna taa " * 1000
        result = normalizer(long_text)
        assert len(result) > 0

    def test_unicode_normalization_forms(self):
        normalizer = BambaraNormalizer()
        nfc = unicodedata.normalize("NFC", "é")
        nfd = unicodedata.normalize("NFD", "é")
        assert normalizer(nfc) == normalizer(nfd)
