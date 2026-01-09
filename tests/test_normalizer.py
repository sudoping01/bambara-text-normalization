import unicodedata

import pytest

from bambara_normalizer import (
    BambaraEvaluator,
    BambaraNormalizer,
    BambaraNormalizerConfig,
    analyze_text,
    bambara_to_number,
    compute_cer,
    compute_wer,
    create_normalizer,
    denormalize_numbers_in_text,
    evaluate,
    get_base_char,
    get_tone,
    has_tone_marks,
    is_bambara_char,
    is_bambara_special_char,
    normalize,
    normalize_numbers_in_text,
    number_to_bambara,
    remove_tones,
    validate_bambara_text,
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

    # @pytest.mark.skip(reason="Number expansion disabled")
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


class TestNewDisambiguationCases:
    """
    New test cases for k' and n' disambiguation based on user feedback.

    These test cases handle:
    1. k' followed by another k' contraction
    2. Lookahead expansion of contractions (t' → tɛ)
    3. n' → na disambiguation (come to) vs ni (conjunction)
    4. k'i and k'o pronoun handling
    """

    def test_k_followed_by_k_contraction_ke(self):
        """k'o k'a la → ka o kɛ a la (first k' defaults, second k' sees postposition)"""
        normalizer = BambaraNormalizer()
        assert normalizer("Ka na son k'o k'a la") == "ka na son ka o kɛ a la"

    def test_k_with_ma_ko_reported_speech(self):
        """Ne k'a ma ko ayi → Ne ko a ma ko ayi"""
        normalizer = BambaraNormalizer()
        assert normalizer("Ne k'a ma ko ayi") == "ne ko a ma ko ayi"

    def test_k_ale_with_expanded_contraction_lookahead(self):
        """K'ale t'a fɛ k'a kɛ → Ko ale tɛ a fɛ ka a kɛ

        - K'ale: lookahead is t'a, which expands to tɛ (clause marker) → ko
        - k'a kɛ: lookahead is kɛ (verb), not a clause marker → ka
        """
        normalizer = BambaraNormalizer()
        assert normalizer("K'ale t'a fɛ k'a kɛ") == "ko ale tɛ a fɛ ka a kɛ"

    def test_n_contraction_na_come_to(self):
        """N'ala son n'a ma → Ni ala son na a ma

        - First n'ala: no 'ma' follows → ni (conjunction)
        - Second n'a ma: 'ma' follows → na (come to)
        """
        normalizer = BambaraNormalizer()
        assert normalizer("N'ala son n'a ma") == "ni ala son na a ma"

    def test_k_i_pronoun_with_clause_marker(self):
        """K'i k'i janto i yɛrɛ la → Ko i ka i janto i yɛrɛ la

        - First K'i: lookahead is k'i which predicts to ka (clause marker) → ko
        - Second k'i: lookahead is janto (regular verb) → ka
        """
        normalizer = BambaraNormalizer()
        assert normalizer("K'i k'i janto i yɛrɛ la") == "ko i ka i janto i yɛrɛ la"

    def test_k_o_pronoun_basic(self):
        """Test k'o with various following words"""
        normalizer = BambaraNormalizer()
        # k'o followed by postposition → kɛ
        assert normalizer("k'o la") == "kɛ o la"
        # k'o followed by verb → ka
        assert normalizer("k'o ta") == "ka o ta"

    def test_k_i_pronoun_basic(self):
        """Test k'i with various following words"""
        normalizer = BambaraNormalizer()
        # k'i followed by postposition → kɛ
        assert normalizer("k'i la") == "kɛ i la"
        # k'i followed by verb → ka
        assert normalizer("k'i ta") == "ka i ta"
        # k'i followed by clause marker → ko
        assert normalizer("k'i ka taa") == "ko i ka taa"

    def test_n_disambiguation_ni_default(self):
        """n' defaults to ni when not followed by pronoun + ma"""
        normalizer = BambaraNormalizer()
        assert normalizer("n'a ta") == "ni a ta"
        assert normalizer("n'i bɛ") == "ni i bɛ"

    def test_n_disambiguation_na_with_ma(self):
        """n' + pronoun + ma → na (come to)"""
        normalizer = BambaraNormalizer()
        assert normalizer("n'a ma") == "na a ma"
        assert normalizer("n'i ma") == "na i ma"
        assert normalizer("n'u ma") == "na u ma"

    def test_complex_sentence_multiple_contractions(self):
        """Test sentence with multiple different contractions"""
        normalizer = BambaraNormalizer()
        # "Come to him and say to them that they should take it"
        result = normalizer("N'a ma k'u ka a ta")
        assert "na a ma" in result
        assert "ko u ka" in result


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
        evaluator = BambaraEvaluator(config=BambaraNormalizerConfig.preserving_tones())
        result = evaluator.evaluate("fɔ́", "fɔ̀", compute_diacritic_rate=True)
        # DER is now implemented - should detect tone difference
        assert result.der is not None
        assert result.der > 0  # Different tones should give non-zero DER


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
        # Check that we found a contraction containing b'
        assert any("b'" in c for c in analysis['contractions_found'])


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


class TestContractionModes:
    def test_expand_mode_default(self):
        normalizer = BambaraNormalizer()
        assert normalizer("b'a fɔ") == "bɛ a fɔ"

    def test_expand_mode_explicit(self):
        config = BambaraNormalizerConfig(contraction_mode="expand")
        normalizer = BambaraNormalizer(config)
        assert normalizer("b'a fɔ") == "bɛ a fɔ"
        assert normalizer("k'a ta") == "ka a ta"
        assert normalizer("k'a la") == "kɛ a la"

    def test_contract_mode_simple(self):
        config = BambaraNormalizerConfig(contraction_mode="contract")
        normalizer = BambaraNormalizer(config)
        assert normalizer("bɛ a fɔ") == "b'a fɔ"
        assert normalizer("tɛ a don") == "t'a don"
        assert normalizer("ye a fɔ") == "y'a fɔ"

    def test_contract_mode_k_variants(self):
        config = BambaraNormalizerConfig(contraction_mode="contract")
        normalizer = BambaraNormalizer(config)
        assert normalizer("ka a ta") == "k'a ta"
        assert normalizer("kɛ a la") == "k'a la"
        assert normalizer("ko an ka") == "k'an ka"

    def test_contract_mode_n_variants(self):
        config = BambaraNormalizerConfig(contraction_mode="contract")
        normalizer = BambaraNormalizer(config)
        assert normalizer("ni a ta") == "n'a ta"
        assert normalizer("na a ma") == "n'a ma"

    def test_preserve_mode_keeps_contracted(self):
        config = BambaraNormalizerConfig(contraction_mode="preserve")
        normalizer = BambaraNormalizer(config)
        assert normalizer("b'a fɔ") == "b'a fɔ"
        assert normalizer("k'a ta") == "k'a ta"

    def test_preserve_mode_keeps_expanded(self):
        config = BambaraNormalizerConfig(contraction_mode="preserve")
        normalizer = BambaraNormalizer(config)
        assert normalizer("bɛ a fɔ") == "bɛ a fɔ"
        assert normalizer("ka a ta") == "ka a ta"

    def test_contract_mode_complex_sentence(self):
        config = BambaraNormalizerConfig(contraction_mode="contract")
        normalizer = BambaraNormalizer(config)
        result = normalizer("ko u ka a ta")
        assert "k'u" in result
        assert "k'a" in result

    def test_round_trip_expand_contract(self):
        expand_config = BambaraNormalizerConfig(contraction_mode="expand")
        contract_config = BambaraNormalizerConfig(contraction_mode="contract")
        expand_normalizer = BambaraNormalizer(expand_config)
        contract_normalizer = BambaraNormalizer(contract_config)

        original = "b'a fɔ"
        expanded = expand_normalizer(original)  # "bɛ a fɔ"
        contracted = contract_normalizer(expanded)  # "b'a fɔ"
        assert contracted == original

    def test_create_normalizer_with_mode(self):
        normalizer = create_normalizer("wer", mode="contract")
        assert normalizer("bɛ a fɔ") == "b'a fɔ"

    def test_normalize_convenience_with_mode(self):
        assert normalize("b'a fɔ", mode="expand") == "bɛ a fɔ"
        assert normalize("bɛ a fɔ", mode="contract") == "b'a fɔ"
        assert normalize("b'a fɔ", mode="preserve") == "b'a fɔ"


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


class TestNumberNormalization:

    def test_number_to_bambara_units(self):
        assert number_to_bambara(0) == "fu"
        assert number_to_bambara(1) == "kelen"
        assert number_to_bambara(5) == "duuru"
        assert number_to_bambara(9) == "kɔnɔntɔn"

    def test_number_to_bambara_tens(self):
        assert number_to_bambara(10) == "tan"
        assert number_to_bambara(15) == "tan ni duuru"
        assert number_to_bambara(20) == "mugan"
        assert number_to_bambara(25) == "mugan ni duuru"

    def test_number_to_bambara_hundreds(self):
        assert number_to_bambara(100) == "kɛmɛ"
        assert number_to_bambara(123) == "kɛmɛ ni mugan ni saba"
        assert number_to_bambara(200) == "kɛmɛ fila"
        assert number_to_bambara(500) == "kɛmɛ duuru"

    def test_number_to_bambara_thousands(self):
        assert number_to_bambara(1000) == "waa kelen"
        assert number_to_bambara(5000) == "waa duuru"
        assert number_to_bambara(10000) == "waa tan"

    def test_number_to_bambara_millions(self):
        assert number_to_bambara(1000000) == "miliyɔn kelen"

    def test_number_to_bambara_decimal(self):
        assert number_to_bambara(5.3) == "duuru tomi saba"

    def test_bambara_to_number_units(self):
        assert bambara_to_number("fu") == 0
        assert bambara_to_number("kelen") == 1
        assert bambara_to_number("duuru") == 5

    def test_bambara_to_number_compound(self):
        assert bambara_to_number("tan ni duuru") == 15
        assert bambara_to_number("kɛmɛ ni mugan ni saba") == 123
        assert bambara_to_number("waa kelen") == 1000

    def test_bambara_to_number_decimal(self):
        assert bambara_to_number("duuru tomi saba") == 5.3

    def test_normalize_numbers_in_text(self):
        assert normalize_numbers_in_text("A ye 5 wari di") == "A ye duuru wari di"
        assert normalize_numbers_in_text("Mɔgɔ 100 nana") == "Mɔgɔ kɛmɛ nana"

    def test_denormalize_numbers_in_text(self):
        assert denormalize_numbers_in_text("A ye duuru wari di") == "A ye 5 wari di"
        assert denormalize_numbers_in_text("Mɔgɔ kɛmɛ nana") == "Mɔgɔ 100 nana"

    def test_normalizer_with_expand_numbers(self):
        result = normalize("A ye 5 wari di", expand_numbers=True)
        assert "duuru" in result
        assert "5" not in result

    def test_normalizer_without_expand_numbers(self):
        from bambara_normalizer import normalize
        result = normalize("A ye 5 wari di", expand_numbers=False)
        assert "5" in result
        assert "duuru" not in result

    def test_wer_preset_expands_numbers(self):
        from bambara_normalizer import BambaraNormalizer, BambaraNormalizerConfig
        config = BambaraNormalizerConfig.for_wer_evaluation()
        normalizer = BambaraNormalizer(config)
        result = normalizer("A ye 100 sɔrɔ")
        assert "kɛmɛ" in result

    def test_round_trip_number_conversion(self):
        for n in [0, 1, 5, 10, 15, 20, 42, 100, 123, 500, 1000, 5000]:
            bambara = number_to_bambara(n)
            back = bambara_to_number(bambara)
            assert back == n, f"Round trip failed for {n}: {bambara} -> {back}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])