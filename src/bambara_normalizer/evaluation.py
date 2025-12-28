from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

import jiwer
from jiwer import transforms as tr

from .normalizer import BambaraNormalizer, BambaraNormalizerConfig
from .config import EvaluationResult


class BambaraTransform(tr.AbstractTransform):
    def __init__(self, normalizer: BambaraNormalizer):
        self.normalizer = normalizer

    def process_string(self, s: str) -> str:
        return self.normalizer(s)
    
    def process_list(self, inp: List[str]) -> List[str]:
        return [self.process_string(s) for s in inp]


def create_bambara_transform(
    normalizer: Optional[BambaraNormalizer] = None,
    config: Optional[BambaraNormalizerConfig] = None,
    preset: str = "wer"
) -> tr.Compose:
    if normalizer is None:
        if config:
            normalizer = BambaraNormalizer(config)
        else:
            presets = {
                "wer": BambaraNormalizerConfig.for_wer_evaluation,
                "cer": BambaraNormalizerConfig.for_cer_evaluation,
                "standard": BambaraNormalizerConfig,
            }
            normalizer = BambaraNormalizer(presets.get(preset, BambaraNormalizerConfig)())

    return tr.Compose([
        BambaraTransform(normalizer),
        tr.RemoveMultipleSpaces(),
        tr.Strip(),
        tr.ReduceToListOfListOfWords(),
    ])


def create_bambara_char_transform(
    normalizer: Optional[BambaraNormalizer] = None,
    config: Optional[BambaraNormalizerConfig] = None,
    preset: str = "cer"
) -> tr.Compose:
    if normalizer is None:
        if config:
            normalizer = BambaraNormalizer(config)
        else:
            presets = {
                "wer": BambaraNormalizerConfig.for_wer_evaluation,
                "cer": BambaraNormalizerConfig.for_cer_evaluation,
                "standard": BambaraNormalizerConfig,
            }
            normalizer = BambaraNormalizer(presets.get(preset, BambaraNormalizerConfig)())

    return tr.Compose([
        BambaraTransform(normalizer),
        tr.RemoveMultipleSpaces(),
        tr.Strip(),
        tr.ReduceToListOfListOfChars(),
    ])


def compute_wer(
    reference: Union[str, List[str]],
    hypothesis: Union[str, List[str]],
    normalizer: Optional[BambaraNormalizer] = None
) -> float:
    transform = create_bambara_transform(normalizer) if normalizer else None
    return jiwer.wer(
        reference, 
        hypothesis,
        reference_transform=transform,
        hypothesis_transform=transform
    )


def compute_cer(
    reference: Union[str, List[str]],
    hypothesis: Union[str, List[str]],
    normalizer: Optional[BambaraNormalizer] = None
) -> float:
    transform = create_bambara_char_transform(normalizer) if normalizer else None
    return jiwer.cer(
        reference,
        hypothesis,
        reference_transform=transform,
        hypothesis_transform=transform
    )


def compute_mer(
    reference: Union[str, List[str]],
    hypothesis: Union[str, List[str]],
    normalizer: Optional[BambaraNormalizer] = None
) -> float:
    transform = create_bambara_transform(normalizer) if normalizer else None
    return jiwer.mer(
        reference,
        hypothesis,
        reference_transform=transform,
        hypothesis_transform=transform
    )


def compute_wil(
    reference: Union[str, List[str]],
    hypothesis: Union[str, List[str]],
    normalizer: Optional[BambaraNormalizer] = None
) -> float:
    transform = create_bambara_transform(normalizer) if normalizer else None
    return jiwer.wil(
        reference,
        hypothesis,
        reference_transform=transform,
        hypothesis_transform=transform
    )


def compute_wip(
    reference: Union[str, List[str]],
    hypothesis: Union[str, List[str]],
    normalizer: Optional[BambaraNormalizer] = None
) -> float:
    """Compute Word Information Preserved using jiwer."""
    transform = create_bambara_transform(normalizer) if normalizer else None
    return jiwer.wip(
        reference, 
        hypothesis,
        reference_transform=transform,
        hypothesis_transform=transform
    )


def compute_der(
    reference: str,
    hypothesis: str,
    normalizer: Optional[BambaraNormalizer] = None
) -> float:
    """Compute Diacritic Error Rate (DER).
    """
    if normalizer:
        reference = normalizer(reference)
        hypothesis = normalizer(hypothesis)

    def extract_diacritics(text: str) -> List[str]:

        result = []
        normalized = unicodedata.normalize('NFD', text)
        for char in normalized:
            if unicodedata.category(char) == 'Mn':
                result.append(char)
            elif char.isalpha():
                result.append('')
        return result

    ref_diacritics = extract_diacritics(reference)
    hyp_diacritics = extract_diacritics(hypothesis)

    if len(ref_diacritics) == 0:
        return 0.0 if len(hyp_diacritics) == 0 else float('inf')

    errors = 0
    for ref_d, hyp_d in zip(ref_diacritics, hyp_diacritics):
        if ref_d != hyp_d:
            errors += 1

    errors += abs(len(ref_diacritics) - len(hyp_diacritics))

    return errors / len(ref_diacritics)


def evaluate(
    reference: str,
    hypothesis: str,
    normalizer: Optional[BambaraNormalizer] = None,
    compute_diacritic_rate: bool = False
) -> EvaluationResult:
    """Comprehensive ASR evaluation with normalization.
    
    Args:
        reference: Reference transcription
        hypothesis: Hypothesis transcription  
        normalizer: Optional normalizer to apply
        compute_diacritic_rate: Whether to compute DER
        
    Returns:
        EvaluationResult with all metrics
    """
 
    word_transform = create_bambara_transform(normalizer) if normalizer else None
    char_transform = create_bambara_char_transform(normalizer) if normalizer else None
    
    ref_norm = normalizer(reference) if normalizer else reference
    hyp_norm = normalizer(hypothesis) if normalizer else hypothesis
    
    word_output = jiwer.process_words(
        reference,
        hypothesis,
        reference_transform=word_transform,
        hypothesis_transform=word_transform
    )
    
    char_output = jiwer.process_characters(
        reference,
        hypothesis,
        reference_transform=char_transform,
        hypothesis_transform=char_transform
    )
    
    der = None
    if compute_diacritic_rate:
        if normalizer and normalizer.config.preserve_tones:
            der = compute_der(reference, hypothesis, normalizer)
        else:
            der = compute_der(reference, hypothesis)
    
    return EvaluationResult(
        wer=word_output.wer,
        cer=char_output.cer,
        mer=word_output.mer,
        wil=word_output.wil,
        wip=word_output.wip,
        der=der,
        word_substitutions=word_output.substitutions,
        word_deletions=word_output.deletions,
        word_insertions=word_output.insertions,
        word_hits=word_output.hits,
        total_reference_words=sum(len(ref) for ref in word_output.references),
        char_substitutions=char_output.substitutions,
        char_deletions=char_output.deletions,
        char_insertions=char_output.insertions,
        char_hits=char_output.hits,
        total_reference_chars=sum(len(ref) for ref in char_output.references),
        reference_normalized=ref_norm,
        hypothesis_normalized=hyp_norm,
    )


def evaluate_batch(
    references: List[str],
    hypotheses: List[str],
    normalizer: Optional[BambaraNormalizer] = None,
    compute_diacritic_rate: bool = False
) -> Tuple[EvaluationResult, List[EvaluationResult]]:

    if len(references) != len(hypotheses):
        raise ValueError("Reference and hypothesis lists must have same length")
    
    word_transform = create_bambara_transform(normalizer) if normalizer else None
    char_transform = create_bambara_char_transform(normalizer) if normalizer else None
    
    word_output = jiwer.process_words(
        references,
        hypotheses,
        reference_transform=word_transform,
        hypothesis_transform=word_transform
    )
    
    char_output = jiwer.process_characters(
        references,
        hypotheses,
        reference_transform=char_transform,
        hypothesis_transform=char_transform
    )
    
    individual_results = []
    der_sum = 0.0
    der_count = 0
    
    for ref, hyp in zip(references, hypotheses):
        result = evaluate(ref, hyp, normalizer, compute_diacritic_rate)
        individual_results.append(result)
        
        if result.der is not None and result.der != float('inf'):
            der_sum += result.der
            der_count += 1
    
    aggregate_der = der_sum / der_count if der_count > 0 else None
    
    aggregate_result = EvaluationResult(
        wer=word_output.wer,
        cer=char_output.cer,
        mer=word_output.mer,
        wil=word_output.wil,
        wip=word_output.wip,
        der=aggregate_der,
        word_substitutions=word_output.substitutions,
        word_deletions=word_output.deletions,
        word_insertions=word_output.insertions,
        word_hits=word_output.hits,
        total_reference_words=sum(len(ref) for ref in word_output.references),
        char_substitutions=char_output.substitutions,
        char_deletions=char_output.deletions,
        char_insertions=char_output.insertions,
        char_hits=char_output.hits,
        total_reference_chars=sum(len(ref) for ref in char_output.references),
    )
    
    return aggregate_result, individual_results


def visualize_alignment(
    reference: str,
    hypothesis: str,
    normalizer: Optional[BambaraNormalizer] = None
) -> str:
    transform = create_bambara_transform(normalizer) if normalizer else None

    word_output = jiwer.process_words(
        reference,
        hypothesis,
        reference_transform=transform,
        hypothesis_transform=transform
    )

    return jiwer.visualize_alignment(word_output)


class BambaraEvaluator:
    """Convenience class for consistent ASR evaluation with Bambara normalization.

    Example:
        >>> evaluator = BambaraEvaluator()
        >>> result = evaluator.evaluate("B'a fɔ́", "BƐ a fɔ")
        >>> print(result)
        WER: 0.00% ...
    """

    def __init__(
        self,
        config: Optional[BambaraNormalizerConfig] = None,
        preset: str = "wer"
    ):
        if config:
            self.normalizer = BambaraNormalizer(config)
        else:
            presets = {
                "wer": BambaraNormalizerConfig.for_wer_evaluation,
                "cer": BambaraNormalizerConfig.for_cer_evaluation,
                "standard": BambaraNormalizerConfig,
            }
            self.normalizer = BambaraNormalizer(presets.get(preset, BambaraNormalizerConfig)())


        self.transform = create_bambara_transform(self.normalizer)

    def evaluate(
        self,
        reference: str,
        hypothesis: str,
        compute_diacritic_rate: bool = False
    ) -> EvaluationResult:
        return evaluate(reference, hypothesis, self.normalizer, compute_diacritic_rate)

    def evaluate_batch(
        self,
        references: List[str],
        hypotheses: List[str],
        compute_diacritic_rate: bool = False
    ) -> Tuple[EvaluationResult, List[EvaluationResult]]:
        return evaluate_batch(references, hypotheses, self.normalizer, compute_diacritic_rate)

    def wer(self, reference: Union[str, List[str]], hypothesis: Union[str, List[str]]) -> float:
        return jiwer.wer(reference, hypothesis, 
                        truth_transform=self.transform, 
                        hypothesis_transform=self.transform)

    def cer(self, reference: Union[str, List[str]], hypothesis: Union[str, List[str]]) -> float:
        return jiwer.cer(reference, hypothesis,
                        truth_transform=self.transform,
                        hypothesis_transform=self.transform)

    def visualize(self, reference: str, hypothesis: str) -> str:
        return visualize_alignment(reference, hypothesis, self.normalizer)

    def normalize(self, text: str) -> str:
        return self.normalizer(text)
