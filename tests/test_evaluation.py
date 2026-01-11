import pytest

from bambara_normalizer import (
    BambaraEvaluator,
    BambaraNormalizerConfig,
    compute_cer,
    compute_wer,
    evaluate,
)


class TestWERCalculation:
    def test_identical_after_normalization(self, wer_normalizer):
        ref = "B'a fɔ́"
        hyp = "BƐ a fɔ"
        wer = compute_wer(ref, hyp, wer_normalizer)
        assert wer_normalizer(ref) == wer_normalizer(hyp)
        assert wer == 0.0

    def test_wer_with_errors(self, normalizer):
        ref = "n bɛ taa"
        hyp = "n bɛ na"
        wer = compute_wer(ref, hyp, normalizer)
        assert wer == pytest.approx(1 / 3)

    def test_wer_deletion(self, normalizer):
        ref = "a b c"
        hyp = "a c"
        result = evaluate(ref, hyp, normalizer)
        assert result.word_deletions == 1

    def test_wer_insertion(self, normalizer):
        ref = "a c"
        hyp = "a b c"
        result = evaluate(ref, hyp, normalizer)
        assert result.word_insertions == 1


class TestCERCalculation:
    def test_cer_identical(self, normalizer):
        cer = compute_cer("test", "test", normalizer)
        assert cer == 0.0

    def test_cer_with_errors(self, normalizer):
        ref = "abc"
        hyp = "abd"
        cer = compute_cer(ref, hyp, normalizer)
        assert cer == pytest.approx(1 / 3)


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

    def test_evaluator_with_der(self, tone_preserving_normalizer):
        evaluator = BambaraEvaluator(config=BambaraNormalizerConfig.preserving_tones())
        result = evaluator.evaluate("fɔ́", "fɔ̀", compute_diacritic_rate=True)
        assert result.der is not None
        assert result.der > 0

    def test_evaluator_with_mode(self):
        evaluator = BambaraEvaluator(mode="contract")
        result = evaluator.evaluate("bɛ a fɔ", "bɛ a fɔ")
        assert result.wer == 0.0
