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

    def test_k_disambiguation_to_ke_with_postpositions(self):
        normalizer = BambaraNormalizer()
        assert normalizer("k'a la") == "kɛ a la"
        assert normalizer("k'a ye") == "kɛ a ye"
        assert normalizer("k'a fɛ") == "kɛ a fɛ"
        assert normalizer("E de ye nin k'a la wa") == "e de ye nin kɛ a la wa"

    def test_k_disambiguation_to_ka_with_verbs(self):
        normalizer = BambaraNormalizer()
        assert normalizer("k'a ta") == "ka a ta"
        assert normalizer("k'a fɔ") == "ka a fɔ"
        assert normalizer("k'a di") == "ka a di"
        assert normalizer("k'a dun") == "ka a dun"
        assert normalizer("nin ta k'a di Musa ma") == "nin ta ka a di musa ma"

    def test_k_disambiguation_ke_benefactive_with_ma(self):
        normalizer = BambaraNormalizer()
        # k' + ma + NOUN + ye → kɛ (benefactive: "be X for someone")
        assert normalizer("k'a ma hɛrɛ ye") == "kɛ a ma hɛrɛ ye"
        assert normalizer("k'a ma tasuma ye") == "kɛ a ma tasuma ye"
        assert normalizer("k'u ma hɛrɛ ye") == "kɛ u ma hɛrɛ ye"
        assert normalizer("k'a ma yɛrɛ ye") == "kɛ a ma yɛrɛ ye"
        assert normalizer("k'u ma yɛrɛ ye") == "kɛ u ma yɛrɛ ye"
        assert normalizer("Nin ka k'a ma tasuma ye") == "nin ka kɛ a ma tasuma ye"

    def test_k_disambiguation_to_ko_with_clause_markers(self):
        normalizer = BambaraNormalizer()
        assert normalizer("k'an kana da a la") == "ko an kana da a la"
        assert normalizer("k'an ka ta so") == "ko an ka ta so"
        assert normalizer("k'u ka na") == "ko u ka na"
        assert normalizer("k'anw kana") == "ko anw kana"
        assert normalizer("k'ale yɛrɛ de y'a k'a la") == "ko ale yɛrɛ de ye a kɛ a la"

    def test_k_disambiguation_ko_full_sentences(self):
        normalizer = BambaraNormalizer()
        result = normalizer("A kɛ Ala kama i ka taa fɔ k'u ka na")
        assert "ko u ka na" in result

    def test_k_disambiguation_mixed_sentence(self):
        normalizer = BambaraNormalizer()
        # k'anw + ma + ko (clause marker) → ko (reported speech)
        result = normalizer("Musa k'anw ma ko Ameriki kadi")
        assert "ko anw ma" in result

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
        assert "́" in unicodedata.normalize('NFD', result) or "̀" in unicodedata.normalize('NFD', result)

    def test_remove_tones_config(self):
        config = BambaraNormalizerConfig.for_wer_evaluation()
        normalizer = BambaraNormalizer(config)
        result = normalizer("fɔ́lɔ̀")
        decomposed = unicodedata.normalize('NFD', result)
        assert '\u0301' not in decomposed
        assert '\u0300' not in decomposed

    @pytest.mark.skip(reason="Number expansion disabled")
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
        assert result == unicodedata.normalize('NFC', result)


class TestKDisambiguation:

    def test_ke_postposition_la(self):
        normalizer = BambaraNormalizer()
        assert normalizer("k'a la") == "kɛ a la"

    def test_ke_benefactive_ma_noun_ye(self):
        """Test benefactive: k' + ma + NOUN + ye → kɛ"""
        normalizer = BambaraNormalizer()
        assert normalizer("k'a ma hɛrɛ ye") == "kɛ a ma hɛrɛ ye"
        assert normalizer("k'a ma tasuma ye") == "kɛ a ma tasuma ye"
        assert normalizer("k'a ma yɛrɛ ye") == "kɛ a ma yɛrɛ ye"
        assert normalizer("k'u ma yɛrɛ ye") == "kɛ u ma yɛrɛ ye"

    def test_ko_ma_reported_speech(self):
        """Test reported speech: k' + ma + CLAUSE_MARKER → ko"""
        normalizer = BambaraNormalizer()
        assert normalizer("k'anw ma ko Ameriki kadi") == "ko anw ma ko ameriki kadi"

    def test_ke_postposition_ye(self):
        normalizer = BambaraNormalizer()
        assert normalizer("k'a ye") == "kɛ a ye"

    def test_ke_postposition_fe(self):
        normalizer = BambaraNormalizer()
        assert normalizer("k'a fɛ") == "kɛ a fɛ"

    def test_ke_in_sentence(self):
        normalizer = BambaraNormalizer()
        assert normalizer("E de ye nin k'a la wa") == "e de ye nin kɛ a la wa"

    def test_ke_benefactive_full_sentence(self):
        normalizer = BambaraNormalizer()
        assert normalizer("Nin ka k'a ma tasuma ye") == "nin ka kɛ a ma tasuma ye"

    def test_ka_verb_ta(self):
        normalizer = BambaraNormalizer()
        assert normalizer("k'a ta") == "ka a ta"

    def test_ka_verb_fo(self):
        normalizer = BambaraNormalizer()
        assert normalizer("k'a fɔ") == "ka a fɔ"

    def test_ka_verb_di(self):
        normalizer = BambaraNormalizer()
        assert normalizer("k'a di") == "ka a di"

    def test_ka_verb_dun(self):
        normalizer = BambaraNormalizer()
        assert normalizer("k'a dun") == "ka a dun"

    def test_ka_in_sentence(self):
        normalizer = BambaraNormalizer()
        assert normalizer("nin ta k'a di Musa ma") == "nin ta ka a di musa ma"

    def test_ko_marker_kana(self):
        normalizer = BambaraNormalizer()
        assert normalizer("k'an kana") == "ko an kana"

    def test_ko_marker_ka(self):
        normalizer = BambaraNormalizer()
        assert normalizer("k'an ka ta so") == "ko an ka ta so"

    def test_ko_marker_u_ka(self):
        normalizer = BambaraNormalizer()
        assert normalizer("k'u ka na") == "ko u ka na"

    def test_ko_marker_anw_kana(self):
        normalizer = BambaraNormalizer()
        assert normalizer("k'anw kana") == "ko anw kana"

    def test_ko_emphatic_yere(self):
        normalizer = BambaraNormalizer()
        result = normalizer("k'ale yɛrɛ de y'a k'a la")
        assert "ko ale" in result
        assert "kɛ a la" in result

    def test_ko_full_sentence_1(self):
        normalizer = BambaraNormalizer()
        result = normalizer("A kɛ Ala kama i ka taa fɔ k'u ka na")
        assert "ko u ka na" in result

    def test_multiple_k_contractions(self):
        normalizer = BambaraNormalizer()
        result = normalizer("k'ale yɛrɛ de y'a k'a la")
        assert "ko ale" in result
        assert "kɛ a la" in result

    def test_ka_no_lookahead(self):
        normalizer = BambaraNormalizer()
        assert normalizer("k'a") == "ka a"


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
        nfc = unicodedata.normalize('NFC', 'é')
        nfd = unicodedata.normalize('NFD', 'é')
        assert normalizer(nfc) == normalizer(nfd)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])