"""
Bambara (Bamanankan) Text Normalizer for ASR Evaluation

A production-grade text normalizer specifically designed for Bambara language,
handling contractions, special characters, tone marks, legacy orthography,
and other linguistic features that affect WER/CER calculations.

Basic Usage:
    >>> from bambara_normalizer import BambaraNormalizer
    >>> normalizer = BambaraNormalizer()
    >>> normalizer("B'a fɔ́!")
    'bɛ a fɔ'

For WER Evaluation:
    >>> from bambara_normalizer import BambaraNormalizer, BambaraNormalizerConfig
    >>> normalizer = BambaraNormalizer(BambaraNormalizerConfig.for_wer_evaluation())
    >>> normalizer("Ń t'à lɔ̀n!")
    'n tɛ a lɔn'

With Evaluation Metrics:
    >>> from bambara_normalizer import BambaraEvaluator
    >>> evaluator = BambaraEvaluator()
    >>> result = evaluator.evaluate("B'a fɔ́", "BƐ a fɔ")
    >>> print(f"WER: {result.wer:.2%}, CER: {result.cer:.2%}")
"""

__version__ = "1.0.0"
__author__ = "Claude (Anthropic)"
__license__ = "MIT"

from .normalizer import (
    BambaraNormalizer,
    BambaraNormalizerConfig,
    # NormalizationLevel,
    create_normalizer,
)

from .evaluation import (
    BambaraEvaluator,
    BambaraTransform,
    EvaluationResult,
    compute_wer,
    compute_cer,
    compute_der,
    compute_mer,
    compute_wil,
    compute_wip,
    create_bambara_transform,
    evaluate,
    evaluate_batch,
    visualize_alignment,
)

from .utils import (
    is_bambara_char,
    is_bambara_special_char,
    get_base_char,
    get_tone,
    add_tone,
    remove_tones,
    has_tone_marks,
    count_tone_marks,
    validate_bambara_text,
    analyze_text,
    normalize_unicode_variants,
    get_unicode_info,
    BAMBARA_VOWELS,
    BAMBARA_CONSONANTS,
    BAMBARA_SPECIAL_CHARS,
    BAMBARA_ALPHABET,
)

__all__ = [
    'BambaraNormalizer',
    'BambaraNormalizerConfig',
    'NormalizationLevel',
    'BambaraEvaluator',
    'EvaluationResult',
    'create_normalizer',
    'compute_wer',
    'compute_cer',
    'compute_der',
    'compute_mer',
    'compute_wil',
    'compute_wip',
    'evaluate',
    'evaluate_batch',
    'visualize_alignment',
    'create_bambara_transform',
    'BambaraTransform',
    
    'is_bambara_char',
    'is_bambara_special_char',
    'get_base_char',
    'get_tone',
    'add_tone',
    'remove_tones',
    'has_tone_marks',
    'count_tone_marks',
    'validate_bambara_text',
    'analyze_text',
    'normalize_unicode_variants',
    'get_unicode_info',
    
    'BAMBARA_VOWELS',
    'BAMBARA_CONSONANTS',
    'BAMBARA_SPECIAL_CHARS',
    'BAMBARA_ALPHABET',
]


def normalize(text: str, preset: str = "standard", **kwargs) -> str:
    """Convenience function for quick normalization.
    
    Args:
        text: Text to normalize
        preset: Preset configuration ("standard", "wer", "cer", "minimal")
        **kwargs: Override specific configuration options
        
    Returns:
        Normalized text
        
    Example:
        >>> from bambara_normalizer import normalize
        >>> normalize("B'a fɔ́!")
        'bɛ a fɔ'
        >>> normalize("B'a fɔ́!", preset="wer")
        'bɛ a fɔ'
    """
    normalizer = create_normalizer(preset, **kwargs)
    return normalizer(text)



__all__.append('normalize')
