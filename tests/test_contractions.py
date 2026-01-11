from bambara_normalizer import (
    BambaraNormalizer,
    BambaraNormalizerConfig,
    create_normalizer,
    normalize,
)


class TestContractionExpansion:
    def test_expansion_ba(self, normalizer):
        assert normalizer("An b'a fɔ Ala ni ce.") == "an bɛ a fɔ ala ni ce"
        assert normalizer("b'a") == "bɛ a"

    def test_expansion_ta(self, normalizer):
        assert normalizer("n t'a don") == "n tɛ a don"

    def test_expansion_ya(self, normalizer):
        assert normalizer("A y'a fɔ") == "a ye a fɔ"

    def test_expansion_na(self, normalizer):
        result = normalizer("i n'i ce")
        assert "ni" in result

    def test_expansion_ka_default(self, normalizer):
        result = normalizer("k'a dun")
        assert "ka" in result

    def test_multiple_contractions(self, normalizer):
        result = normalizer("Ń b'i fɛ, n t'a don")
        assert "bɛ" in result
        assert "tɛ" in result


class TestContractionModes:
    def test_expand_mode_default(self, normalizer):
        assert normalizer("b'a fɔ") == "bɛ a fɔ"

    def test_expand_mode_explicit(self):
        config = BambaraNormalizerConfig(contraction_mode="expand")
        normalizer = BambaraNormalizer(config)
        assert normalizer("b'a fɔ") == "bɛ a fɔ"
        assert normalizer("k'a ta") == "ka a ta"
        assert normalizer("k'a la") == "kɛ a la"

    def test_contract_mode_simple(self, contract_normalizer):
        assert contract_normalizer("bɛ a fɔ") == "b'a fɔ"
        assert contract_normalizer("tɛ a don") == "t'a don"
        assert contract_normalizer("ye a fɔ") == "y'a fɔ"

    def test_contract_mode_k_variants(self, contract_normalizer):
        assert contract_normalizer("ka a ta") == "k'a ta"
        assert contract_normalizer("kɛ a la") == "k'a la"
        assert contract_normalizer("ko an ka") == "k'an ka"

    def test_contract_mode_n_variants(self, contract_normalizer):
        assert contract_normalizer("ni a ta") == "n'a ta"
        assert contract_normalizer("na a ma") == "n'a ma"

    def test_preserve_mode_keeps_contracted(self, preserve_normalizer):
        assert preserve_normalizer("b'a fɔ") == "b'a fɔ"
        assert preserve_normalizer("k'a ta") == "k'a ta"

    def test_preserve_mode_keeps_expanded(self, preserve_normalizer):
        assert preserve_normalizer("bɛ a fɔ") == "bɛ a fɔ"
        assert preserve_normalizer("ka a ta") == "ka a ta"

    def test_contract_mode_complex_sentence(self, contract_normalizer):
        result = contract_normalizer("ko u ka a ta")
        assert "k'u" in result
        assert "k'a" in result

    def test_round_trip_expand_contract(self):
        expand_normalizer = BambaraNormalizer(BambaraNormalizerConfig(contraction_mode="expand"))
        contract_normalizer = BambaraNormalizer(
            BambaraNormalizerConfig(contraction_mode="contract")
        )

        original = "b'a fɔ"
        expanded = expand_normalizer(original)
        contracted = contract_normalizer(expanded)
        assert contracted == original

    def test_create_normalizer_with_mode(self):
        normalizer = create_normalizer("wer", mode="contract")
        assert normalizer("bɛ a fɔ") == "b'a fɔ"

    def test_normalize_convenience_with_mode(self):
        assert normalize("b'a fɔ", mode="expand") == "bɛ a fɔ"
        assert normalize("bɛ a fɔ", mode="contract") == "b'a fɔ"
        assert normalize("b'a fɔ", mode="preserve") == "b'a fɔ"
