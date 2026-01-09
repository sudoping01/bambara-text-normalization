
# Copyright 2026 sudoping01.

# Licensed under the MIT License; you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:

# https://opensource.org/licenses/MIT

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__version__ = "1.0.0"
__author__ = "sudoping01"
__license__ = "MIT"



from .evaluation import (
    BambaraEvaluator,
    BambaraTransform,
    EvaluationResult,
    compute_cer,
    compute_der,
    compute_mer,
    compute_wer,
    compute_wil,
    compute_wip,
    create_bambara_transform,
    evaluate,
    evaluate_batch,
    visualize_alignment,
)
from .normalizer import (
    BambaraNormalizer,
    BambaraNormalizerConfig,
    create_normalizer,
)
from .numbers import (
    bambara_to_number,
    denormalize_numbers_in_text,
    is_number_word,
    normalize_numbers_in_text,
    number_to_bambara,
    number_to_ordinal,
)
from .utils import (
    BAMBARA_ALPHABET,
    BAMBARA_CONSONANTS,
    BAMBARA_SPECIAL_CHARS,
    BAMBARA_VOWELS,
    add_tone,
    analyze_text,
    count_tone_marks,
    get_base_char,
    get_tone,
    get_unicode_info,
    has_tone_marks,
    is_bambara_char,
    is_bambara_special_char,
    normalize_unicode_variants,
    remove_tones,
    validate_bambara_text,
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


    "number_to_bambara",
    "bambara_to_number",
    "normalize_numbers_in_text",
    "denormalize_numbers_in_text",
    "is_number_word",
    "number_to_ordinal",

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
