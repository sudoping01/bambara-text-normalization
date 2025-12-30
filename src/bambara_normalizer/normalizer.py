from __future__ import annotations

import re
import unicodedata
from typing import Optional, Dict, List

from .config import BambaraNormalizerConfig


class BambaraNormalizer:
    """Bambara text normalization.

    Handles Bambara-specific linguistic features including:
    - Special characters: ɛ, ɔ, ɲ, ŋ
    - Grammatical contractions: b', t', y', n', k' (with disambiguation)
    - Tone diacritics: à, á, è, é, etc.
    - Legacy orthography: è→ɛ, ny→ɲ, ng→ŋ

    Example:
        >>> normalizer = BambaraNormalizer()
        >>> normalizer("B'a fɔ́!")
        'bɛ a fɔ'

        >>> normalizer = BambaraNormalizer(BambaraNormalizerConfig.for_wer_evaluation())
        >>> normalizer("Ń t'à lɔ̀n")
        'n tɛ a lɔn'
    """


    SPECIAL_CHARS = {
        'ɛ': '\u025B',
        'Ɛ': '\u0190',
        'ɔ': '\u0254',
        'Ɔ': '\u0186',
        'ɲ': '\u0272',
        'Ɲ': '\u019D',
        'ŋ': '\u014B',
        'Ŋ': '\u014A',
    }


    APOSTROPHE_VARIANTS = [
        '\u0027',
        '\u2019',
        '\u02BC',
        '\u2018',
        '\u0060',
        '\u00B4',
        '\u2032', 
        '\uFF07', 
        '\u02B9', 
        '\u02BB',
    ]

    # =========================================================================
    # POSTPOSITIONS (closed class - from Daba grammar)
    # Used for k' disambiguation: k' + vowel + PP → kɛ (verb "to do")
    # =========================================================================
    POSTPOSITIONS = {
        'la', 'na',
        'ma',
        'ye',
        'fɛ',
        'kɔnɔ',
        'kan',
        'kɔ',
        'kɔrɔ',
        'da', 'daa',
        'kun',
        'ɲɛ', 'ɲɛɛ',
        'bolo',
        'sɛmɛ',
        'cɛ', 'cɛma',
        'kosɔn',
        'yɛrɛ',
    }


    SIMPLE_CONTRACTIONS = {
        "b'": "bɛ ",
        "t'": "tɛ ",
        "y'": "ye ",
        "n'": "ni ",
        "m'": "ma ",
        "s'": "sa ",
    }


    EXTENDED_CONTRACTIONS = {
        "b'a": "bɛ a",
        "t'a": "tɛ a",
        "y'a": "ye a",
        "n'a": "ni a",
        "b'i": "bɛ i",
        "t'i": "tɛ i",
        "y'i": "ye i",
        "n'i": "ni i",
        "b'o": "bɛ o",
        "t'o": "tɛ o",
        "n'o": "ni o",
        "n'u": "ni u",
        "b'u": "bɛ u",
        "t'u": "tɛ u",
        "y'o": "ye o",
        "y'u": "ye u",
    }

    """
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    BAMBARA k' CONTRACTION DISAMBIGUATION RULES
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    The contraction k' can come from TWO different sources:
    1. ka (infinitive marker)
    2. kɛ (verb "to do/make/happen")

    RULE: Look at what follows k' + vowel

    CASE 1: INFINITIVE MARKER (ka)
    Pattern: k' + vowel + VERB
    Examples:
        K'a ta     → ka a ta    "to take it"
        K'a fɔ     → ka a fɔ    "to say it"
        K'i ye     → ka i ye    "to see you"

    CASE 2: VERB kɛ (to do/make)
    Pattern: k' + vowel + POSTPOSITION
    Examples:
        k'a la     → kɛ a la    "do it there"
        k'a ma     → kɛ a ma    "do it to him"
        k'a ye     → kɛ a ye    "make it as"

    SUMMARY:
        k' + vowel + VERB          →  ka (infinitive marker)
        k' + vowel + POSTPOSITION  →  kɛ (verb "to do")
        k' + vowel + OTHER         →  ka (default - infinitive more common)
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """


    LEGACY_ORTHOGRAPHY = {
        'è': 'ɛ',
        'È': 'Ɛ',
        'ò': 'ɔ',
        'Ò': 'Ɔ',
        'ê': 'ɛ',
        'Ê': 'Ɛ',
        'ô': 'ɔ',
        'Ô': 'Ɔ',
        'ε': 'ɛ',
        'э': 'ɛ',
    }

    LEGACY_DIGRAPHS = {
        'ny': 'ɲ',
        'Ny': 'Ɲ',
        'NY': 'Ɲ',
        'ng': 'ŋ',
        'Ng': 'Ŋ',
        'NG': 'Ŋ',
    }

    SENEGALESE_VARIANTS = {
        'ñ': 'ɲ',
        'Ñ': 'Ɲ',
    }


    TONE_DIACRITICS = {
        '\u0300',  
        '\u0301', 
        '\u030C', 
        '\u0302',  
        '\u0304',  
    }

    PUNCTUATION_CATEGORIES = {'Po', 'Ps', 'Pe', 'Pi', 'Pf', 'Pd', 'Pc'}


    def __init__(self, config: Optional[BambaraNormalizerConfig] = None):
        self.config = config or BambaraNormalizerConfig()
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        apostrophe_chars = ''.join(re.escape(c) for c in self.APOSTROPHE_VARIANTS)
        self._apostrophe_pattern = re.compile(f'[{apostrophe_chars}]')
        self._whitespace_pattern = re.compile(r'\s+')
        self._repetition_pattern = re.compile(r'(.)\1{2,}')
        self._number_pattern = re.compile(r'\d+')
        self._build_punctuation_pattern()

    def _build_punctuation_pattern(self) -> None:
        punct_chars = []
        for i in range(0x10000):
            char = chr(i)
            if unicodedata.category(char) in self.PUNCTUATION_CATEGORIES:
                if char not in self.APOSTROPHE_VARIANTS:
                    punct_chars.append(char)
        self._punctuation_pattern = re.compile(
            f'[{"".join(re.escape(c) for c in punct_chars)}]'
        )


    def __call__(self, text: str) -> str:
        return self.normalize(text)

    def normalize(self, text: str) -> str:
        if not text:
            return ""

        text = unicodedata.normalize('NFC', text)

        if self.config.normalize_apostrophes:
            text = self._normalize_apostrophes(text)

        if self.config.expand_contractions:
            text = self._expand_contractions(text)

        if self.config.normalize_legacy_orthography:
            text = self._normalize_legacy_orthography(text)

        if self.config.normalize_special_chars:
            text = self._normalize_special_chars(text)

        if self.config.lowercase:
            text = self._lowercase(text)

        if not self.config.preserve_tones:
            text = self._remove_tone_marks(text)
        elif self.config.remove_diacritics_except_tones:
            text = self._remove_non_tone_diacritics(text)

        if self.config.remove_punctuation:
            text = self._remove_punctuation(text)

        if self.config.strip_repetitions:
            text = self._strip_repetitions(text)

        if self.config.normalize_compounds:
            text = self._normalize_compounds(text)

        if self.config.normalize_whitespace:
            text = self._normalize_whitespace(text)

        return text


    def _normalize_apostrophes(self, text: str) -> str:
        return self._apostrophe_pattern.sub("'", text)


    def _expand_contractions(self, text: str) -> str:
        """
        Expand Bambara contractions.
        - b' → bɛ
        - t' → tɛ
        - y' → ye
        - n' → ni
        - m' → ma
        - k' → ka OR kɛ (disambiguated by following word)
        """

        text = self._expand_k_contraction(text)
        for contracted, expanded in self.EXTENDED_CONTRACTIONS.items():
            pattern = re.compile(re.escape(contracted), re.IGNORECASE)
            text = pattern.sub(expanded, text)

        for contracted, expanded in self.SIMPLE_CONTRACTIONS.items():
            pattern = re.compile(re.escape(contracted), re.IGNORECASE)
            text = pattern.sub(expanded, text)

        return text

    def _expand_k_contraction(self, text: str) -> str:
        """
        Rules (from Daba grammar analysis):
        - k' + vowel + POSTPOSITION → kɛ + vowel (verb "to do/make")
        - k' + vowel + VERB/OTHER → ka + vowel (infinitive marker)

        Examples:
            k'a la   → kɛ a la   (do it there)
            k'a ta   → ka a ta  (to take it)
            k'a fɔ   → ka a fɔ  (to say it)
            k'a ma   → kɛ a ma  (do it to him)
        """
        words = text.split()
        result = []
        i = 0

        while i < len(words):
            word = words[i]

            k_match = re.match(r"k'([aeiouɛɔ])(.*)", word, re.IGNORECASE)

            if k_match:
                vowel = k_match.group(1)
                remainder = k_match.group(2) or ""

                if i + 1 < len(words):
                    next_word = words[i + 1]
                    next_word_base = self._strip_tones_and_punct(next_word.lower())

                    if next_word_base in self.POSTPOSITIONS:
                        expanded = f"kɛ {vowel}{remainder}"
                    else:
                        expanded = f"ka {vowel}{remainder}"
                else:
                    expanded = f"ka {vowel}{remainder}"

                result.append(expanded)
            else:
                result.append(word)

            i += 1

        return ' '.join(result)

    def _strip_tones(self, word: str) -> str:
        nfd = unicodedata.normalize('NFD', word)
        return ''.join(c for c in nfd if c not in self.TONE_DIACRITICS)

    def _strip_tones_and_punct(self, word: str) -> str:
        nfd = unicodedata.normalize('NFD', word)
        word = ''.join(c for c in nfd if c not in self.TONE_DIACRITICS)
        word = unicodedata.normalize('NFC', word)
        return ''.join(c for c in word if unicodedata.category(c) not in self.PUNCTUATION_CATEGORIES)


    def _normalize_legacy_orthography(self, text: str) -> str:
        for old, new in self.LEGACY_DIGRAPHS.items():
            text = text.replace(old, new)

        for old, new in self.LEGACY_ORTHOGRAPHY.items():
            text = text.replace(old, new)

        for old, new in self.SENEGALESE_VARIANTS.items():
            text = text.replace(old, new)

        return text


    def _normalize_special_chars(self, text: str) -> str:
        result = []
        for char in text:
            if char in 'εЄє':
                result.append('ɛ')
            elif char in 'ΕЭэ':
                result.append('Ɛ')
            else:
                result.append(char)
        return ''.join(result)


    def _lowercase(self, text: str) -> str:
        return text.lower()

    def _remove_tone_marks(self, text: str) -> str:
        text = unicodedata.normalize('NFD', text)
        result = [c for c in text if c not in self.TONE_DIACRITICS]
        return unicodedata.normalize('NFC', ''.join(result))

    def _remove_non_tone_diacritics(self, text: str) -> str:
        text = unicodedata.normalize('NFD', text)
        result = []
        for char in text:
            category = unicodedata.category(char)
            if category != 'Mn' or char in self.TONE_DIACRITICS:
                result.append(char)
        return unicodedata.normalize('NFC', ''.join(result))


    def _remove_punctuation(self, text: str) -> str:
        return self._punctuation_pattern.sub('', text)


    def _strip_repetitions(self, text: str) -> str:
        return self._repetition_pattern.sub(r'\1\1', text)

    def _normalize_compounds(self, text: str) -> str:
        compounds = [
            (r'\b(bi)\s+(saba|naani|duuru|wɔɔrɔ|wolonwula|segin|kɔnɔntɔn)\b', r'\1\2'),
            (r'\b(tan)\s+(ni)\s+', r'\1 \2 '),
        ]
        for pattern, replacement in compounds:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    def _normalize_whitespace(self, text: str) -> str:
        return self._whitespace_pattern.sub(' ', text).strip()

    def normalize_for_comparison(self, text: str) -> str:
        original_config = self.config
        self.config = BambaraNormalizerConfig.for_wer_evaluation()
        result = self.normalize(text)
        self.config = original_config
        return result

    def normalize_batch(self, texts: List[str]) -> List[str]:
        return [self.normalize(text) for text in texts]

    def get_normalization_diff(self, text: str) -> Dict[str, str]:
        result = {'original': text}

        text = unicodedata.normalize('NFC', text)
        result['nfc_normalized'] = text

        if self.config.normalize_apostrophes:
            text = self._normalize_apostrophes(text)
            result['apostrophes_normalized'] = text

        if self.config.expand_contractions:
            text = self._expand_contractions(text)
            result['contractions_expanded'] = text

        if self.config.normalize_legacy_orthography:
            text = self._normalize_legacy_orthography(text)
            result['legacy_normalized'] = text

        if self.config.lowercase:
            text = self._lowercase(text)
            result['lowercased'] = text

        if not self.config.preserve_tones:
            text = self._remove_tone_marks(text)
            result['tones_removed'] = text

        if self.config.remove_punctuation:
            text = self._remove_punctuation(text)
            result['punctuation_removed'] = text

        if self.config.normalize_whitespace:
            text = self._normalize_whitespace(text)
            result['whitespace_normalized'] = text

        result['final'] = text
        return result



def create_normalizer(preset: str = "standard", **kwargs) -> BambaraNormalizer:
    """
    Factory function to create a normalizer with preset configuration.

    Args:
        preset: One of "standard", "wer", "cer", "preserving_tones", "minimal"
        **kwargs: Override specific configuration options

    Returns:
        Configured BambaraNormalizer instance.

    Example:
        >>> normalizer = create_normalizer("wer", preserve_tones=True)
    """
    presets = {
        "standard": BambaraNormalizerConfig,
        "wer": BambaraNormalizerConfig.for_wer_evaluation,
        "cer": BambaraNormalizerConfig.for_cer_evaluation,
        "preserving_tones": BambaraNormalizerConfig.preserving_tones,
        "minimal": BambaraNormalizerConfig.minimal,
    }

    if preset not in presets:
        raise ValueError(f"Unknown preset: {preset}. Choose from: {list(presets.keys())}")

    config = presets[preset]()

    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            raise ValueError(f"Unknown configuration option: {key}")

    return BambaraNormalizer(config)