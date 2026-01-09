
# Copyright 2026 sudoping01.

# Licensed under the MIT License; you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:

# https://opensource.org/licenses/MIT

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import unicodedata

import jiwer
from jiwer import transforms as tr

from .config import BambaraNormalizerConfig, EvaluationResult
from .normalizer import BambaraNormalizer


class BambaraTransform(tr.AbstractTransform):

    def __init__(self, normalizer: BambaraNormalizer):
        self.normalizer = normalizer

    def process_string(self, s: str) -> str:
        return self.normalizer(s)

    def process_list(self, inp: list[str]) -> list[str]:
        return [self.process_string(s) for s in inp]


def create_bambara_transform(
    normalizer: BambaraNormalizer | None = None,
    config: BambaraNormalizerConfig | None = None,
    preset: str = "wer",
    mode: str = "expand"
) -> tr.Compose:
    """
    Create a jiwer transform pipeline with Bambara normalization.

    Args:
        normalizer: Optional pre-configured normalizer
        config: Optional configuration (ignored if normalizer provided)
        preset: Preset name if no normalizer/config provided
        mode: Contraction mode ("expand", "contract", "preserve")

    Returns:
        Composed jiwer transform
    """
    if normalizer is None:
        if config:
            normalizer = BambaraNormalizer(config)
        else:
            presets = {
                "wer": BambaraNormalizerConfig.for_wer_evaluation,
                "cer": BambaraNormalizerConfig.for_cer_evaluation,
                "standard": BambaraNormalizerConfig,
            }
            preset_func = presets.get(preset, BambaraNormalizerConfig)
            if preset in ("wer", "cer"):
                config = preset_func(mode=mode)
            else:
                config = preset_func()
                config.contraction_mode = mode
            normalizer = BambaraNormalizer(config)

    return tr.Compose([
        BambaraTransform(normalizer),
        tr.RemoveMultipleSpaces(),
        tr.Strip(),
        tr.ReduceToListOfListOfWords(),
    ])


def create_bambara_char_transform(
    normalizer: BambaraNormalizer | None = None,
    config: BambaraNormalizerConfig | None = None,
    preset: str = "cer",
    mode: str = "expand"
) -> tr.Compose:
    """
    Create a jiwer character-level transform pipeline with Bambara normalization.

    Args:
        normalizer: Optional pre-configured normalizer
        config: Optional configuration (ignored if normalizer provided)
        preset: Preset name if no normalizer/config provided
        mode: Contraction mode ("expand", "contract", "preserve")

    Returns:
        Composed jiwer transform for character-level metrics
    """
    if normalizer is None:
        if config:
            normalizer = BambaraNormalizer(config)
        else:
            presets = {
                "wer": BambaraNormalizerConfig.for_wer_evaluation,
                "cer": BambaraNormalizerConfig.for_cer_evaluation,
                "standard": BambaraNormalizerConfig,
            }
            preset_func = presets.get(preset, BambaraNormalizerConfig)
            if preset in ("wer", "cer"):
                config = preset_func(mode=mode)
            else:
                config = preset_func()
                config.contraction_mode = mode
            normalizer = BambaraNormalizer(config)

    return tr.Compose([
        BambaraTransform(normalizer),
        tr.RemoveMultipleSpaces(),
        tr.Strip(),
        tr.ReduceToListOfListOfChars(),
    ])


def compute_wer(
    reference: str | list[str],
    hypothesis: str | list[str],
    normalizer: BambaraNormalizer | None = None,
    mode: str = "expand"
) -> float:
    """
    Compute Word Error Rate with Bambara normalization.

    Args:
        reference: Reference transcription(s)
        hypothesis: Hypothesis transcription(s)
        normalizer: Optional pre-configured normalizer
        mode: Contraction mode if no normalizer provided

    Returns:
        WER as float (0.0 to 1.0+)
    """
    transform = create_bambara_transform(normalizer, mode=mode) if normalizer else create_bambara_transform(mode=mode)
    return jiwer.wer(
        reference,
        hypothesis,
        reference_transform=transform,
        hypothesis_transform=transform
    )


def compute_cer(
    reference: str | list[str],
    hypothesis: str | list[str],
    normalizer: BambaraNormalizer | None = None,
    mode: str = "expand"
) -> float:
    """
    Compute Character Error Rate with Bambara normalization.

    Args:
        reference: Reference transcription(s)
        hypothesis: Hypothesis transcription(s)
        normalizer: Optional pre-configured normalizer
        mode: Contraction mode if no normalizer provided

    Returns:
        CER as float (0.0 to 1.0+)
    """
    transform = create_bambara_char_transform(normalizer, mode=mode) if normalizer else create_bambara_char_transform(mode=mode)
    return jiwer.cer(
        reference,
        hypothesis,
        reference_transform=transform,
        hypothesis_transform=transform
    )


def compute_mer(
    reference: str | list[str],
    hypothesis: str | list[str],
    normalizer: BambaraNormalizer | None = None,
    mode: str = "expand"
) -> float:
    """
    Compute Match Error Rate with Bambara normalization.

    Args:
        reference: Reference transcription(s)
        hypothesis: Hypothesis transcription(s)
        normalizer: Optional pre-configured normalizer
        mode: Contraction mode if no normalizer provided

    Returns:
        MER as float
    """
    transform = create_bambara_transform(normalizer, mode=mode) if normalizer else create_bambara_transform(mode=mode)
    return jiwer.mer(
        reference,
        hypothesis,
        reference_transform=transform,
        hypothesis_transform=transform
    )


def compute_wil(
    reference: str | list[str],
    hypothesis: str | list[str],
    normalizer: BambaraNormalizer | None = None,
    mode: str = "expand"
) -> float:
    """
    Compute Word Information Lost with Bambara normalization.

    Args:
        reference: Reference transcription(s)
        hypothesis: Hypothesis transcription(s)
        normalizer: Optional pre-configured normalizer
        mode: Contraction mode if no normalizer provided

    Returns:
        WIL as float
    """
    transform = create_bambara_transform(normalizer, mode=mode) if normalizer else create_bambara_transform(mode=mode)
    return jiwer.wil(
        reference,
        hypothesis,
        reference_transform=transform,
        hypothesis_transform=transform
    )


def compute_wip(
    reference: str | list[str],
    hypothesis: str | list[str],
    normalizer: BambaraNormalizer | None = None,
    mode: str = "expand"
) -> float:
    """
    Compute Word Information Preserved with Bambara normalization.

    Args:
        reference: Reference transcription(s)
        hypothesis: Hypothesis transcription(s)
        normalizer: Optional pre-configured normalizer
        mode: Contraction mode if no normalizer provided

    Returns:
        WIP as float
    """
    transform = create_bambara_transform(normalizer, mode=mode) if normalizer else create_bambara_transform(mode=mode)
    return jiwer.wip(
        reference,
        hypothesis,
        reference_transform=transform,
        hypothesis_transform=transform
    )


def compute_der(
    reference: str,
    hypothesis: str,
    normalizer: BambaraNormalizer | None = None
) -> float:
    """
    Compute Diacritic Error Rate (DER).

    Measures how well tone marks are preserved/recognized.
    Only meaningful when preserve_tones=True in normalizer config.

    Args:
        reference: Reference transcription
        hypothesis: Hypothesis transcription
        normalizer: Optional normalizer to apply first

    Returns:
        DER as float (0.0 = perfect, higher = worse)
    """
    if normalizer:
        reference = normalizer(reference)
        hypothesis = normalizer(hypothesis)

    def extract_diacritics(text: str) -> list[str]:
        result = []
        normalized = unicodedata.normalize('NFD', text)
        for char in normalized:
            if unicodedata.category(char) == 'Mn':
                result.append(char)
            elif char.isalpha():
                result.append('')  # Placeholder for no diacritic
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
    normalizer: BambaraNormalizer | None = None,
    compute_diacritic_rate: bool = False,
    mode: str = "expand"
) -> EvaluationResult:
    """
    Comprehensive ASR evaluation with Bambara normalization.

    Args:
        reference: Reference transcription
        hypothesis: Hypothesis transcription
        normalizer: Optional normalizer to apply
        compute_diacritic_rate: Whether to compute DER
        mode: Contraction mode if no normalizer provided

    Returns:
        EvaluationResult with all metrics
    """

    if normalizer is None:
        config = BambaraNormalizerConfig.for_wer_evaluation(mode=mode)
        normalizer = BambaraNormalizer(config)

    word_transform = create_bambara_transform(normalizer)
    char_transform = create_bambara_char_transform(normalizer)

    ref_norm = normalizer(reference)
    hyp_norm = normalizer(hypothesis)

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
        if normalizer.config.preserve_tones:
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
    references: list[str],
    hypotheses: list[str],
    normalizer: BambaraNormalizer | None = None,
    compute_diacritic_rate: bool = False,
    mode: str = "expand"
) -> tuple[EvaluationResult, list[EvaluationResult]]:
    """
    Evaluate a batch of reference-hypothesis pairs.

    Args:
        references: List of reference transcriptions
        hypotheses: List of hypothesis transcriptions
        normalizer: Optional normalizer to apply
        compute_diacritic_rate: Whether to compute DER
        mode: Contraction mode if no normalizer provided

    Returns:
        Tuple of (aggregate_result, individual_results)
    """
    if len(references) != len(hypotheses):
        raise ValueError("Reference and hypothesis lists must have same length")

    if normalizer is None:
        config = BambaraNormalizerConfig.for_wer_evaluation(mode=mode)
        normalizer = BambaraNormalizer(config)

    word_transform = create_bambara_transform(normalizer)
    char_transform = create_bambara_char_transform(normalizer)

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
    normalizer: BambaraNormalizer | None = None,
    mode: str = "expand"
) -> str:
    """
    Visualize word alignment between reference and hypothesis.

    Args:
        reference: Reference transcription
        hypothesis: Hypothesis transcription
        normalizer: Optional normalizer to apply
        mode: Contraction mode if no normalizer provided

    Returns:
        String visualization of alignment
    """
    if normalizer is None:
        config = BambaraNormalizerConfig.for_wer_evaluation(mode=mode)
        normalizer = BambaraNormalizer(config)

    transform = create_bambara_transform(normalizer)

    word_output = jiwer.process_words(
        reference,
        hypothesis,
        reference_transform=transform,
        hypothesis_transform=transform
    )

    return jiwer.visualize_alignment(word_output)


class BambaraEvaluator:
    """
    Convenience class for consistent ASR evaluation with Bambara normalization.

    Supports three contraction modes:
    - "expand": Expand contractions (b'a → bɛ a) - default
    - "contract": Contract expanded forms (bɛ a → b'a)
    - "preserve": Don't touch contractions

    Example:
        >>> evaluator = BambaraEvaluator()
        >>> result = evaluator.evaluate("B'a fɔ́", "BƐ a fɔ")
        >>> print(result)
        WER: 0.00% ...

        >>> # Use contract mode for fair comparison
        >>> evaluator = BambaraEvaluator(mode="contract")
        >>> result = evaluator.evaluate("k'a ta", "ka a ta")
        >>> print(result.wer)  # 0.0 - same after contraction
    """

    def __init__(
        self,
        config: BambaraNormalizerConfig | None = None,
        preset: str = "wer",
        mode: str = "expand"
    ):
        """
        Initialize the evaluator.

        Args:
            config: Optional configuration (overrides preset and mode)
            preset: Preset name ("wer", "cer", "standard")
            mode: Contraction mode ("expand", "contract", "preserve")
        """
        if config:
            self.normalizer = BambaraNormalizer(config)
        else:
            presets = {
                "wer": BambaraNormalizerConfig.for_wer_evaluation,
                "cer": BambaraNormalizerConfig.for_cer_evaluation,
                "standard": BambaraNormalizerConfig,
            }
            preset_func = presets.get(preset, BambaraNormalizerConfig.for_wer_evaluation)
            if preset in ("wer", "cer"):
                config = preset_func(mode=mode)
            else:
                config = preset_func()
                config.contraction_mode = mode
            self.normalizer = BambaraNormalizer(config)

        self.transform = create_bambara_transform(self.normalizer)
        self.char_transform = create_bambara_char_transform(self.normalizer)

    @property
    def mode(self) -> str:
        return self.normalizer.config.contraction_mode

    def evaluate(
        self,
        reference: str,
        hypothesis: str,
        compute_diacritic_rate: bool = False
    ) -> EvaluationResult:
        return evaluate(reference, hypothesis, self.normalizer, compute_diacritic_rate)

    def evaluate_batch(
        self,
        references: list[str],
        hypotheses: list[str],
        compute_diacritic_rate: bool = False
    ) -> tuple[EvaluationResult, list[EvaluationResult]]:
        return evaluate_batch(references, hypotheses, self.normalizer, compute_diacritic_rate)

    def wer(self, reference: str | list[str], hypothesis: str | list[str]) -> float:
        return jiwer.wer(
            reference, hypothesis,
            reference_transform=self.transform,
            hypothesis_transform=self.transform
        )

    def cer(self, reference: str | list[str], hypothesis: str | list[str]) -> float:
        return jiwer.cer(
            reference, hypothesis,
            reference_transform=self.char_transform,
            hypothesis_transform=self.char_transform
        )

    def mer(self, reference: str | list[str], hypothesis: str | list[str]) -> float:
        return jiwer.mer(
            reference, hypothesis,
            reference_transform=self.transform,
            hypothesis_transform=self.transform
        )

    def wil(self, reference: str | list[str], hypothesis: str | list[str]) -> float:
        return jiwer.wil(
            reference, hypothesis,
            reference_transform=self.transform,
            hypothesis_transform=self.transform
        )

    def wip(self, reference: str | list[str], hypothesis: str | list[str]) -> float:
        return jiwer.wip(
            reference, hypothesis,
            reference_transform=self.transform,
            hypothesis_transform=self.transform
        )

    def visualize(self, reference: str, hypothesis: str) -> str:
        return visualize_alignment(reference, hypothesis, self.normalizer)

    def normalize(self, text: str) -> str:
        return self.normalizer(text)