import pytest
import unicodedata
from bambara_normalizer import (
    BambaraNormalizer,
    BambaraNormalizerConfig,
    BambaraEvaluator,
    create_normalizer,
    normalize,
    compute_wer,
    compute_cer,
    evaluate,
    is_bambara_char,
    is_bambara_special_char,
    get_base_char,
    get_tone,
    has_tone_marks,
    remove_tones,
    validate_bambara_text,
    analyze_text,
)


class TestBambaraNormalizer:    
    def test_basic_normalization(self):
        normalizer = BambaraNormalizer()
        assert normalizer("Hello World") == "hello world"
    
    def test_contraction_expansion_ba(self):
        normalizer = BambaraNormalizer()
        assert normalizer("B'a fɔ") == "bɛ a fɔ"
        assert normalizer("b'a") == "bɛ a"
    
    def test_contraction_expansion_ta(self):
        normalizer = BambaraNormalizer()
        assert normalizer("n t'a lon") == "n tɛ a lon"
    
    def test_contraction_expansion_ya(self):
        normalizer = BambaraNormalizer()
        assert normalizer("A y'a fɔ") == "a ye a fɔ"
    
    def test_contraction_expansion_na(self):
        normalizer = BambaraNormalizer()
        result = normalizer("í n'í dén")
        assert "ni" in result  
    
    def test_contraction_expansion_ka(self):
        normalizer = BambaraNormalizer()
        result = normalizer("k'a dún")
        assert "ka" in result  
    
    def test_multiple_contractions(self):
        normalizer = BambaraNormalizer()
        result = normalizer("Ń b'a fɛ, n t'a lon")
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
        result = normalizer("Bɔ́! Taa?")
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
        assert "́" in unicodedata.normalize('NFD', result) or "̀" in unicodedata.normalize('NFD', result)
    
    def test_remove_tones_config(self):
        config = BambaraNormalizerConfig.for_wer_evaluation()
        normalizer = BambaraNormalizer(config)
        result = normalizer("fɔ́lɔ̀")
        decomposed = unicodedata.normalize('NFD', result)
        assert '\u0301' not in decomposed  # acute
        assert '\u0300' not in decomposed  # grave
    
    # def test_number_expansion(self):
    #     config = BambaraNormalizerConfig.for_wer_evaluation()
    #     normalizer = BambaraNormalizer(config)
    #     assert "kelen" in normalizer("1")
    #     assert "fila" in normalizer("2")
    #     assert "tan" in normalizer("10")
    
    def test_empty_string(self):
        normalizer = BambaraNormalizer()
        assert normalizer("") == ""
    
    def test_unicode_nfc_normalization(self):
        normalizer = BambaraNormalizer()
        decomposed = "e\u0301"
        result = normalizer(decomposed)
        assert result == unicodedata.normalize('NFC', result)


class TestNormalizationConfigs:
    
    def test_wer_config(self):
        config = BambaraNormalizerConfig.for_wer_evaluation()
        assert config.expand_contractions is True
        assert config.preserve_tones is False
        assert config.lowercase is True
        assert config.remove_punctuation is True
    
    def test_cer_config(self):
        config = BambaraNormalizerConfig.for_cer_evaluation()
        assert config.expand_contractions is True
        assert config.preserve_tones is False
    
    def test_minimal_config(self):
        config = BambaraNormalizerConfig.minimal()
        assert config.expand_contractions is False
        assert config.preserve_tones is True
    
    def test_create_normalizer_factory(self):
        normalizer = create_normalizer("wer")
        assert isinstance(normalizer, BambaraNormalizer)
        
        normalizer = create_normalizer("standard", preserve_tones=True)
        assert normalizer.config.preserve_tones is True
    
    def test_invalid_preset_raises(self):
        with pytest.raises(ValueError):
            create_normalizer("invalid_preset")


class TestWERCalculation:
    
    def test_identical_after_normalization(self):
        normalizer = BambaraNormalizer(BambaraNormalizerConfig.for_wer_evaluation())
        ref = "B'a fɔ́"
        hyp = "BƐ a fɔ"
        
        wer = compute_wer(ref, hyp, normalizer)
        assert normalizer(ref) == normalizer(hyp)
        assert wer == 0.0
    
    def test_wer_with_errors(self):
        normalizer = BambaraNormalizer()
        ref = "n bɛ taa"
        hyp = "n bɛ na"
        
        wer = compute_wer(ref, hyp, normalizer)
        assert wer == pytest.approx(1/3)
    
    def test_wer_deletion(self):
        normalizer = BambaraNormalizer()
        ref = "a b c"
        hyp = "a c"  
        
        result = evaluate(ref, hyp, normalizer)
        assert result.word_deletions == 1
    
    def test_wer_insertion(self):
        normalizer = BambaraNormalizer()
        ref = "a c"
        hyp = "a b c"  
        
        result = evaluate(ref, hyp, normalizer)
        assert result.word_insertions == 1


class TestCERCalculation:
    
    def test_cer_identical(self):
        normalizer = BambaraNormalizer()
        cer = compute_cer("test", "test", normalizer)
        assert cer == 0.0
    
    def test_cer_with_errors(self):
        normalizer = BambaraNormalizer()
        ref = "abc"
        hyp = "abd" 
        
        cer = compute_cer(ref, hyp, normalizer)
        assert cer == pytest.approx(1/3)


class TestEvaluator:
    def test_evaluator_basic(self):
        evaluator = BambaraEvaluator()
        result = evaluator.evaluate("B'a fɔ", "bɛ a fɔ")
        assert result.wer == 0.0
    
    def test_evaluator_batch(self):
        evaluator = BambaraEvaluator()
        refs = ["a b c", "d e f"]
        hyps = ["a b c", "d e f"]
        
        aggregate, individual = evaluator.evaluate_batch(refs, hyps)
        assert aggregate.wer == 0.0
        assert len(individual) == 2
    
    def test_evaluator_with_der(self):
        evaluator = BambaraEvaluator(BambaraNormalizerConfig.preserving_tones())
        result = evaluator.evaluate("fɔ́", "fɔ̀", compute_diacritic_rate=True)
        assert result.der is not None


class TestUtilityFunctions:
    def test_is_bambara_char(self):
        assert is_bambara_char('a') is True
        assert is_bambara_char('ɛ') is True
        assert is_bambara_char('ŋ') is True
        assert is_bambara_char('q') is False 
    
    def test_is_bambara_special_char(self):
        assert is_bambara_special_char('ɛ') is True
        assert is_bambara_special_char('ɔ') is True
        assert is_bambara_special_char('ɲ') is True
        assert is_bambara_special_char('ŋ') is True
        assert is_bambara_special_char('a') is False
    
    def test_get_base_char(self):
        assert get_base_char('á') == 'a'
        assert get_base_char('ɛ́') == 'ɛ'
        assert get_base_char('a') == 'a'
    
    def test_get_tone(self):
        assert get_tone('á') == 'high'
        assert get_tone('à') == 'low'
        assert get_tone('a') is None
    
    def test_has_tone_marks(self):
        assert has_tone_marks("fɔ́lɔ̀") is True
        assert has_tone_marks("fɔlɔ") is False
    
    def test_remove_tones(self):
        assert remove_tones("fɔ́lɔ̀") == "fɔlɔ"
    
    def test_validate_bambara_text(self):
        is_valid, issues = validate_bambara_text("bɛna")
        assert is_valid is True
        
        is_valid, issues = validate_bambara_text("nyama") 
        assert is_valid is False
        assert len(issues) > 0
    
    def test_analyze_text(self):
        analysis = analyze_text("Ń b'à fɔ́")
        assert 'word_count' in analysis
        assert 'vowel_count' in analysis
        assert 'contractions_found' in analysis
        assert "b'" in analysis['contractions_found']


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
        decomposed = unicodedata.normalize('NFD', result)
        assert '\u0301' in decomposed or '\u0300' in decomposed


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
    
    # def test_code_switching_french(self):
    #     config = BambaraNormalizerConfig()
    #     config.handle_french_loanwords = True
    #     normalizer = BambaraNormalizer(config)
    #     result = normalizer("télé")
    #     assert "tele" in result


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
        
        nfc = unicodedata.normalize('NFC', 'é')
        nfd = unicodedata.normalize('NFD', 'é')
        assert normalizer(nfc) == normalizer(nfd)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
