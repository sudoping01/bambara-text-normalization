from __future__ import annotations

import re
import unicodedata
from typing import Optional, Dict, List

from .config import BambaraNormalizerConfig

class BambaraNormalizer:
    """Bambara text normalizer for ASR evaluation.

    Handles Bambara-specific linguistic features including:
    - Special characters: ɛ, ɔ, ɲ, ŋ
    - Grammatical contractions: b', t', y', n', k'
    - Tone diacritics: à, á, è, é, etc.
    - Legacy orthography: è→ɛ, ny→ɲ, ng→ŋ
    - Number words in Bambara

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
    

    CONTRACTIONS = {
        "b'": "bɛ ",
        "t'": "tɛ ",
        "y'": "ye ",
        "n'": "ni ",
        "k'": "ka ",
        "m'": "ma ",
        "s'": "sa ",
    }
    

    EXTENDED_CONTRACTIONS = {
        "b'a": "bɛ a",
        "t'a": "tɛ a",
        "y'a": "ye a",
        "n'a": "ni a",
        "k'a": "ka a",
        "b'i": "bɛ i",
        "t'i": "tɛ i",
        "y'i": "ye i",
        "n'i": "ni i",
        "k'i": "ka i",
        "b'o": "bɛ o",
        "t'o": "tɛ o",
        "k'o": "ka o",
        "k'u": "ka u",
        # "k'a": "kɛ a", I need to see how I'm gonna handle this one : we can have a k'a la  ==> a kɛ a la
        "n'o": "ni o",
        "n'u": "ni u",


    }

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
    
    # this might not be necessary but let's add it 
    SENEGALESE_VARIANTS = {
        'ñ': 'ɲ',
        'Ñ': 'Ɲ',
    }

   ###################################################
   # I won't use this part for now                   #
   # I need to find a generic way to handle numbers  #
   ###################################################

    NUMBER_WORDS = {
        '0': 'fu',
        '1': 'kelen',
        '2': 'fila',
        '3': 'saba',
        '4': 'naani',
        '5': 'duuru',
        '6': 'wɔɔrɔ',
        '7': 'wolonwula',
        '8': 'segin',
        '9': 'kɔnɔntɔn',
        '10': 'tan',
        '11': 'tan ni kelen',
        '12': 'tan ni fila',
        '13': 'tan ni saba',
        '14': 'tan ni naani',
        '15': 'tan ni duuru',
        '16': 'tan ni wɔɔrɔ',
        '17': 'tan ni wolonwula',
        '18': 'tan ni segin',
        '19': 'tan ni kɔnɔntɔn',
        '20': 'mugan',
        '30': 'bi saba',
        '40': 'bi naani',
        '50': 'bi duuru',
        '60': 'bi wɔɔrɔ',
        '70': 'bi wolonwula',
        '80': 'bi segin',
        '90': 'bi kɔnɔntɔn',
        '100': 'kɛmɛ',
        '1000': 'waa',
    }

    TONE_DIACRITICS = {
        '\u0300',
        '\u0301',
        '\u030C',
        '\u0302',
        '\u0304',
    }

    TONED_VOWELS = {
        'à', 'è', 'ì', 'ò', 'ù', 'ɛ̀', 'ɔ̀',
        'á', 'é', 'í', 'ó', 'ú', 'ɛ́', 'ɔ́',
        'ǎ', 'ě', 'ǐ', 'ǒ', 'ǔ', 'ɛ̌', 'ɔ̌',
        'À', 'È', 'Ì', 'Ò', 'Ù', 'Ɛ̀', 'Ɔ̀',
        'Á', 'É', 'Í', 'Ó', 'Ú', 'Ɛ́', 'Ɔ́',
    }
    

    PUNCTUATION_CATEGORIES = {'Po', 'Ps', 'Pe', 'Pi', 'Pf', 'Pd', 'Pc'}
    
    # It's impossible to handle code switching properly without a full NLP pipeline
    # FRENCH_LOANWORDS = {
    #     'télé': 'tele',
    #     'radio': 'radiyo',
    #     'école': 'lekɔli',
    #     'hôpital': 'ɔpitali',
    #     'monsieur': 'misye',
    #     'madame': 'madam',
    #     'merci': 'mɛrsi',
    #     'bonjour': 'bɔnjur',
    # }
    

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

        self._contraction_patterns = {}
        for contracted, expanded in {**self.CONTRACTIONS, **self.EXTENDED_CONTRACTIONS}.items():
            pattern = re.compile(
                rf"(?:^|(?<=\s))({re.escape(contracted)})",
                re.IGNORECASE
            )
            self._contraction_patterns[pattern] = expanded
    
    def _build_punctuation_pattern(self) -> None:
        punct_chars = []
        for i in range(0x10000): # 1×16^4
            char = chr(i)
            if unicodedata.category(char) in self.PUNCTUATION_CATEGORIES:
                if char not in self.APOSTROPHE_VARIANTS:
                    punct_chars.append(char)
        self._punctuation_pattern = re.compile(f'[{"".join(re.escape(c) for c in punct_chars)}]')
    

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

        # if self.config.handle_french_loanwords:
        #     text = self._normalize_french_loanwords(text)

        if self.config.lowercase:
            text = self._lowercase(text)
    
        if not self.config.preserve_tones:
            text = self._remove_tone_marks(text)
        elif self.config.remove_diacritics_except_tones:
            text = self._remove_non_tone_diacritics(text)
        
        if self.config.remove_punctuation:
            text = self._remove_punctuation(text)
        
        ###########################################
        # I'm closing this section off for now,   #
        # I need to study more NVIDIA ITN rules   #
        ##########################################
        # if self.config.expand_numbers:
        #     text = self._expand_numbers(text)
        
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
             b' ==> bɛ, t' ==> tɛ, y' ==> ye, n' ==> ni, k' ==> ka
        """
        for contracted, expanded in self.EXTENDED_CONTRACTIONS.items():
            pattern = re.compile(re.escape(contracted), re.IGNORECASE)
            text = pattern.sub(expanded, text)

        for contracted, expanded in self.CONTRACTIONS.items():
            pattern = re.compile(re.escape(contracted), re.IGNORECASE)
            text = pattern.sub(expanded, text)
        
        return text
    
    def _normalize_legacy_orthography(self, text: str) -> str:
        """Convert old bambara orthography to modern bambara standard.
        """

        for old, new in self.LEGACY_DIGRAPHS.items():
            text = text.replace(old, new)
        
        for old, new in self.LEGACY_ORTHOGRAPHY.items():
            text = text.replace(old, new)
        
        for old, new in self.SENEGALESE_VARIANTS.items():  # might not be necessay but let's keep it
            text = text.replace(old, new)
        
        return text
    

    ####################################
    # INNEFICIENT BUT I WILL COME BACK #
    ####################################
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
        """Remove all tone diacritics from text.
         This is useful for WER evaluation when tone marking is inconsistent.
        """
        text = unicodedata.normalize('NFD', text)

        result = []
        for char in text:
            if char not in self.TONE_DIACRITICS:
                result.append(char)
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

    # I will reimplement properly this section later
    # def _expand_numbers(self, text: str) -> str:
    #     def replace_number(match: re.Match) -> str:
    #         num_str = match.group(0)

    #         if num_str in self.NUMBER_WORDS:
    #             return self.NUMBER_WORDS[num_str]
           
    #         return ' '.join(self.NUMBER_WORDS.get(d, d) for d in num_str)
        
    #     return self._number_pattern.sub(replace_number, text)


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


def create_normalizer(
    preset: str = "standard",
    **kwargs
) -> BambaraNormalizer:
    """Factory function to create a normalizer with preset configuration.
    
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
