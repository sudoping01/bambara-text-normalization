"""
Bambara (Bamanankan) Text Normalizer for ASR Evaluation.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Optional, Dict, List

from .config import BambaraNormalizerConfig


class BambaraNormalizer:
    """Bambara text normalizer for ASR evaluation.

    Handles Bambara-specific linguistic features including:
    - Special characters: ɛ, ɔ, ɲ, ŋ
    - Grammatical contractions: b', t', y', n', k' (with disambiguation)
    - Tone diacritics: à, á, è, é, etc.
    - Legacy orthography: è==>ɛ, ny==>ɲ, ng==>ŋ

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
    # POSTPOSITIONS COMPATIBLE WITH kɛ (verb "to do/make")
    # Pattern: k' + vowel + KE_POSTPOSITION ==> kɛ
    # These are locative/instrumental postpositions used with "do/make"
    #  'ma' is handled specially - see REPORTED_SPEECH_MARKERS
    # =========================================================================
    KE_POSTPOSITIONS = {
        'la',
        'ye',
        'fɛ',
        'kɔnɔ',
        'kɔ',
        'kɔrɔ',
        'da', 'daa',
        'kun',
        'ɲɛ', 'ɲɛɛ', 'ɲɛfɛ',
        'bolo',
        'sɛmɛ',
        'cɛ', 'cɛma',
        'kɔfɛ',
        'kosɔn', 'kama',
    }

    # =========================================================================
    # REPORTED SPEECH MARKERS (for ko disambiguation after 'ma')
    # When k' + pronoun + ma + REPORTED_SPEECH_MARKER => ko (to say)
    # When k' + pronoun + ma + NOUN + ye ==> kɛ (benefactive)
    # =========================================================================
    REPORTED_SPEECH_MARKERS = {
        'ko',
        'ka',
        'kana',
        'tɛ', 'te',
        'bɛ', 'be',
        'bɛna', 'bena',
        'tɛna', 'tena',
        'tun',
        'mana',
    }

    # =========================================================================
    # CLAUSE MARKERS (closed class: from Daba grammar)
    # Used for k' disambiguation: k' + vowel + MARKER ==> ko (verb "to say")
    # These typically introduce subordinate/reported speech clauses
    # =========================================================================
    CLAUSE_MARKERS = {
        'ka',
        'kana',
        'tɛ', 'te',
        'bɛ', 'be',
        'bɛna', 'bena',
        'tɛna', 'tena',
        'tun',
        'mana',
        'yɛrɛ',
        'de', 'dɛ',
    }

    # =========================================================================
    # SIMPLE CONTRACTIONS (non-k')
    # =========================================================================
    SIMPLE_CONTRACTIONS = {
        "b'": "bɛ ",
        "t'": "tɛ ",
        "y'": "ye ",
        "m'": "ma ",
        "s'": "sa ",
    }

    # =========================================================================
    # EXTENDED CONTRACTIONS (with specific pronouns)
    # Note: n' contractions handled separately for na/ni disambiguation
    # =========================================================================
    EXTENDED_CONTRACTIONS = {
        "b'a": "bɛ a",
        "t'a": "tɛ a",
        "y'a": "ye a",
        "b'i": "bɛ i",
        "t'i": "tɛ i",
        "y'i": "ye i",
        "b'o": "bɛ o",
        "t'o": "tɛ o",
        "y'o": "ye o",
        "y'u": "ye u",
        "b'u": "bɛ u",
        "t'u": "tɛ u",
    }

    # =========================================================================
    # CONTRACTION EXPANSION MAP (for lookahead)
    # Maps contraction prefixes to their expanded forms
    # =========================================================================
    CONTRACTION_EXPANSIONS = {
        "b'": "bɛ",
        "t'": "tɛ",
        "y'": "ye",
        "m'": "ma",
        "s'": "sa",
    }

    """
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    BAMBARA k' CONTRACTION DISAMBIGUATION RULES
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    The contraction k' can come from THREE different sources:
    1. ka (infinitive marker)
    2. kɛ (verb "to do/make/happen")
    3. ko (verb "to say")

    RULE: Look at what follows k' + vowel (the word after the pronoun)

    CASE 1: INFINITIVE MARKER (ka)
    Pattern: k' + vowel + VERB
    Examples:
        k'a ta     ==> ka a ta
        k'a fɔ     ==> ka a fɔ
        k'a dun    ==> ka a dun
        k'a di     ==> ka a di


    CASE 2: VERB kɛ
    Pattern A: k' + vowel + KE_POSTPOSITION (la, ye, fɛ, etc.)
    Examples:
        k'a la     ==> kɛ a la
        k'a ye     ==> kɛ a ye
        k'a fɛ     ==> kɛ a fɛ


    Pattern B: k' + vowel + ma + NOUN + ye (benefactive)
    Examples:
        k'a ma hɛrɛ ye     ==> kɛ a ma hɛrɛ ye
        k'a ma tasuma ye   ==> kɛ a ma tasuma ye
        k'u ma yɛrɛ ye     ==> kɛ u ma yɛrɛ ye


    CASE 3: VERB ko (to say) - reported speech
    Pattern A: k' + vowel + CLAUSE_MARKER (ka, kana, bɛ, tɛ, etc.)
    Examples:
        k'an kana  ==> ko an kana   "said we shouldn't"
        k'an ka ta ==> ko an ka ta  "said we should take"
        k'u ka na  ==> ko u ka na   "said they should come"
        k'ale yɛrɛ ==> ko ale yɛrɛ  "said he himself"


    Pattern B: k' + vowel + ma + REPORTED_SPEECH_MARKER
    Examples:
        k'anw ma ko...  ==> ko anw ma ko...  "said to us that..."

    DISAMBIGUATION PRIORITY:
        1. k' + vowel + ma + X + ye         ==>  kɛ (benefactive)
        2. k' + vowel + ma + SPEECH_MARKER  ==>  ko (reported speech)
        3. k' + vowel + KE_POSTPOSITION     ==>  kɛ (verb "to do")
        4. k' + vowel + CLAUSE_MARKER       ==>  ko (verb "to say")
        5. k' + vowel + OTHER (verb)        ==>  ka (infinitive, DEFAULT)
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

    # this two section may be removed in next version [due to someone disagrement]
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
        # First expand k' contractions (most complex)
        text = self._expand_k_contraction(text)
        
        # Then expand n' contractions (na/ni disambiguation)
        text = self._expand_n_contraction(text)

        # Then other extended contractions
        for contracted, expanded in self.EXTENDED_CONTRACTIONS.items():
            pattern = re.compile(re.escape(contracted), re.IGNORECASE)
            text = pattern.sub(expanded, text)

        # Finally simple contractions
        for contracted, expanded in self.SIMPLE_CONTRACTIONS.items():
            pattern = re.compile(re.escape(contracted), re.IGNORECASE)
            text = pattern.sub(expanded, text)

        return text

    def _get_lookahead_base(self, word: str) -> Optional[str]:
        """
        Get the base form of a word for lookahead disambiguation.
        Expands contractions to their base form.
        Returns None if the word is a k' contraction (needs recursive prediction).
        """
        word_lower = word.lower()
        
        # Check if it's a k' contraction - needs special handling
        if re.match(r"k'[aeiouɛɔ]", word_lower):
            return None  # Signal that we need to predict k' expansion
        
        # Expand other contractions for lookahead
        for prefix, expanded in self.CONTRACTION_EXPANSIONS.items():
            if word_lower.startswith(prefix):
                return expanded
        
        # Regular word - strip tones and punctuation
        return self._strip_tones_and_punct(word_lower)

    def _predict_k_expansion(self, words: List[str], idx: int) -> str:
        """
        Predict what a k' contraction at position idx will expand to.
        Used for recursive lookahead when k' follows k'.
        Returns 'ka', 'kɛ', or 'ko'.
        """
        if idx >= len(words):
            return "ka"
        
        word = words[idx]
        k_match = re.match(r"k'([aeiouɛɔ]\w*)", word, re.IGNORECASE)
        if not k_match:
            return "ka"  # Not a k' contraction
        
        # Look at what follows this k' contraction
        if idx + 1 < len(words):
            next_word = words[idx + 1]
            next_base = self._get_lookahead_base(next_word)
            
            if next_base is None:
                # Next word is also a k' contraction - predict recursively
                predicted_next = self._predict_k_expansion(words, idx + 1)
                if predicted_next == "ka":
                    return "ko"  # ka is clause marker
                else:
                    return "ka"  # kɛ/ko are not clause markers
            
            # Check for postposition
            if next_base in self.KE_POSTPOSITIONS:
                return "kɛ"
            
            # Check for clause marker
            if next_base in self.CLAUSE_MARKERS:
                return "ko"
            
            # Check for ma pattern
            if next_base == 'ma':
                if idx + 2 < len(words):
                    word_after_ma = words[idx + 2]
                    word_after_ma_base = self._strip_tones_and_punct(word_after_ma.lower())
                    
                    # Check for benefactive (ma + X + ye)
                    if idx + 3 < len(words):
                        third_word = words[idx + 3]
                        third_word_base = self._strip_tones_and_punct(third_word.lower())
                        if third_word_base == 'ye':
                            return "kɛ"
                    
                    # Check for reported speech marker after ma
                    if word_after_ma_base in self.REPORTED_SPEECH_MARKERS:
                        return "ko"
                
                return "kɛ"  # Default for ma pattern
        
        return "ka"  # Default

    def _expand_k_contraction(self, text: str) -> str:
        """
        Expand k' contractions with context-aware disambiguation.
        
        Rules (in priority order):
        1. k' + pronoun + ma + X + ye → kɛ (benefactive)
        2. k' + pronoun + ma + SPEECH_MARKER → ko (reported speech)
        3. k' + pronoun + POSTPOSITION → kɛ (do/make)
        4. k' + pronoun + CLAUSE_MARKER → ko (to say)
        5. k' + pronoun + other → ka (infinitive, default)
        """
        words = text.split()
        result = []
        i = 0

        while i < len(words):
            word = words[i]

            k_match = re.match(r"k'([aeiouɛɔ]\w*)", word, re.IGNORECASE)

            if k_match:
                pronoun = k_match.group(1)

                if i + 1 < len(words):
                    next_word = words[i + 1]
                    next_word_base = self._get_lookahead_base(next_word)

                    # Handle case where next word is also a k' contraction
                    if next_word_base is None:
                        # Predict what the next k' will become
                        predicted = self._predict_k_expansion(words, i + 1)
                        if predicted == "ka":
                            # ka is a clause marker → ko
                            expanded = f"ko {pronoun}"
                        else:
                            # kɛ or ko are not clause markers → default ka
                            expanded = f"ka {pronoun}"
                    elif next_word_base == 'ma':
                        # Check for benefactive or reported speech patterns
                        if i + 2 < len(words):
                            word_after_ma = words[i + 2]
                            word_after_ma_base = self._strip_tones_and_punct(word_after_ma.lower())

                            # Check for benefactive: ma + X + ye
                            if i + 3 < len(words):
                                third_word = words[i + 3]
                                third_word_base = self._strip_tones_and_punct(third_word.lower())
                                if third_word_base == 'ye':
                                    expanded = f"kɛ {pronoun}"
                                elif word_after_ma_base in self.REPORTED_SPEECH_MARKERS:
                                    expanded = f"ko {pronoun}"
                                else:
                                    expanded = f"kɛ {pronoun}"
                            elif word_after_ma_base in self.REPORTED_SPEECH_MARKERS:
                                expanded = f"ko {pronoun}"
                            else:
                                expanded = f"kɛ {pronoun}"
                        else:
                            expanded = f"kɛ {pronoun}"
                    elif next_word_base in self.KE_POSTPOSITIONS:
                        expanded = f"kɛ {pronoun}"
                    elif next_word_base in self.CLAUSE_MARKERS:
                        expanded = f"ko {pronoun}"
                    else:
                        expanded = f"ka {pronoun}"
                else:
                    expanded = f"ka {pronoun}"

                result.append(expanded)
            else:
                result.append(word)

            i += 1

        return ' '.join(result)

    def _expand_n_contraction(self, text: str) -> str:
        """
        Expand n' contractions with disambiguation between na (come) and ni (if/and).
        
        Rules:
        1. n' + pronoun + ma → na (come to someone)
        2. n' + other → ni (conjunction, default)
        """
        words = text.split()
        result = []
        i = 0

        while i < len(words):
            word = words[i]

            n_match = re.match(r"n'([aeiouɛɔ]\w*)", word, re.IGNORECASE)

            if n_match:
                pronoun = n_match.group(1)

                if i + 1 < len(words):
                    next_word = words[i + 1]
                    next_word_base = self._strip_tones_and_punct(next_word.lower())

                    if next_word_base == 'ma':
                        # n' + pronoun + ma → na (come to)
                        expanded = f"na {pronoun}"
                    else:
                        # Default: ni (conjunction)
                        expanded = f"ni {pronoun}"
                else:
                    expanded = f"ni {pronoun}"

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