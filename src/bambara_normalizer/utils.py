"""
Utility functions for Bambara text processing.
"""

from __future__ import annotations

import unicodedata
from typing import Dict, List, Optional, Set, Tuple



BAMBARA_VOWELS = set('aeiouɛɔ')
BAMBARA_VOWELS_UPPER = set('AEIOUƐƆ')
BAMBARA_CONSONANTS = set('bcdfghjklmnprstwyzɲŋ')
BAMBARA_CONSONANTS_UPPER = set('BCDFGHJKLMNPRSTWYZƝŊ')
BAMBARA_SPECIAL_CHARS = set('ɛɔɲŋƐƆƝŊ')
BAMBARA_NASAL_VOWELS = {'an', 'en', 'ɛn', 'in', 'on', 'ɔn', 'un'}


TONE_MARKS = {
    '\u0300': 'low',     
    '\u0301': 'high',     
    '\u030C': 'rising',   
    '\u0302': 'falling',  
    '\u0304': 'mid',      
}


BAMBARA_ALPHABET = set('abcdefghijklmnoprstuwyzɛɔɲŋ')


def is_bambara_char(char: str) -> bool:
    base_char = get_base_char(char.lower())
    return base_char in BAMBARA_ALPHABET


def is_bambara_special_char(char: str) -> bool:
    return char in BAMBARA_SPECIAL_CHARS


def get_base_char(char: str) -> str:
    decomposed = unicodedata.normalize('NFD', char)
    return ''.join(c for c in decomposed if unicodedata.category(c) != 'Mn')


def get_tone(char: str) -> Optional[str]:
    decomposed = unicodedata.normalize('NFD', char)
    for c in decomposed:
        if c in TONE_MARKS:
            return TONE_MARKS[c]
    return None


def add_tone(char: str, tone: str) -> str:
    tone_to_mark = {v: k for k, v in TONE_MARKS.items()}
    if tone not in tone_to_mark:
        raise ValueError(f"Unknown tone: {tone}. Valid: {list(TONE_MARKS.values())}")
    
    base = get_base_char(char)
    return unicodedata.normalize('NFC', base + tone_to_mark[tone])


def remove_tones(text: str) -> str:
    decomposed = unicodedata.normalize('NFD', text)
    result = ''.join(c for c in decomposed if c not in TONE_MARKS)
    return unicodedata.normalize('NFC', result)


def has_tone_marks(text: str) -> bool:
    decomposed = unicodedata.normalize('NFD', text)
    return any(c in TONE_MARKS for c in decomposed)


def count_tone_marks(text: str) -> Dict[str, int]:
    decomposed = unicodedata.normalize('NFD', text)
    counts = {tone: 0 for tone in TONE_MARKS.values()}
    for c in decomposed:
        if c in TONE_MARKS:
            counts[TONE_MARKS[c]] += 1
    return counts


def is_nasal_vowel(chars: str) -> bool:
    if len(chars) != 2:
        return False
    return chars.lower() in BAMBARA_NASAL_VOWELS


def split_syllables(word: str) -> List[str]:
    """Basic syllable splitting for Bambara words.
    
    Bambara syllable structure is typically (C)V(N) where:
    - C = consonant (optional onset)
    - V = vowel (required nucleus)
    - N = nasal coda (optional)
    
    This is a simplified implementation.
    
    Args:
        word: Bambara word
        
    Returns:
        List of syllables
    """
    word = word.lower()
    syllables = []
    current = ""
    
    i = 0
    while i < len(word):
        char = word[i]
        
        if char in BAMBARA_CONSONANTS:
            if i + 1 < len(word):
                digraph = word[i:i+2]
                if digraph in ('ny', 'ng', 'sh', 'kh', 'gb', 'gw'):
                    current += digraph
                    i += 2
                    continue
            current += char
            i += 1
            continue
        
        if char in BAMBARA_VOWELS:
            current += char
            if i + 1 < len(word):
                next_char = word[i + 1]
                if next_char == char:
                    current += next_char
                    i += 1
                elif next_char == 'n' and (i + 2 >= len(word) or word[i + 2] not in BAMBARA_VOWELS):
                    current += next_char
                    i += 1
            
            syllables.append(current)
            current = ""
            i += 1
            continue
        
        current += char
        i += 1
    
    if current:
        if syllables:
            syllables[-1] += current
        else:
            syllables.append(current)
    
    return syllables


def validate_bambara_text(text: str) -> Tuple[bool, List[str]]:
    """Validate text for Bambara orthographic compliance.

    Args:
        text: Text to validate

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []

    for i, char in enumerate(text):
        if char.isalpha() and not is_bambara_char(char):
            if char not in 'qvxQVX':
                issues.append(f"Non-Bambara character '{char}' at position {i}")
    
    legacy_patterns = [
        ('ny', 'Should use ɲ instead of ny'),
        ('ng', 'Should use ŋ instead of ng (unless in compound)'),
        ('è', 'Should use ɛ instead of è'),
        ('ò', 'Should use ɔ instead of ò'),
    ]
    text_lower = text.lower()
    for pattern, message in legacy_patterns:
        if pattern in text_lower:
            issues.append(message)
    
    return len(issues) == 0, issues


def normalize_unicode_variants(text: str) -> str:
    """Normalize visually similar but differently encoded characters.
    
    Handles common Unicode confusion issues with Bambara special characters.
    """
    char_map = {
        'ε': 'ɛ',   
        'Ε': 'Ɛ',   
        'є': 'ɛ',   
        'Є': 'Ɛ',   
        'э': 'ɛ',   
        'Э': 'Ɛ', 
        'ᴐ': 'ɔ',   
        'ɳ': 'ŋ',   
        'ñ': 'ɲ', 
        'Ñ': 'Ɲ',
    }
    
    return ''.join(char_map.get(c, c) for c in text)


def get_unicode_info(char: str) -> Dict[str, str]:

    if len(char) != 1:
        char = char[0]
    
    return {
        'character': char,
        'codepoint': f'U+{ord(char):04X}',
        'name': unicodedata.name(char, 'UNKNOWN'),
        'category': unicodedata.category(char),
        'decomposition': unicodedata.decomposition(char) or 'None',
    }


def analyze_text(text: str) -> Dict:
    """Analyze Bambara text for various properties.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with analysis results
    """
    chars = [c for c in text if c.isalpha()]
    words = text.split()
    
    vowels = sum(1 for c in chars if c.lower() in BAMBARA_VOWELS)
    consonants = sum(1 for c in chars if c.lower() in BAMBARA_CONSONANTS)
    special = sum(1 for c in chars if is_bambara_special_char(c))
    
    tone_counts = count_tone_marks(text)
    
    contractions_found = []
    for contraction in ["b'", "t'", "y'", "n'", "k'", "m'"]:
        if contraction in text.lower():
            contractions_found.append(contraction)
    
    is_valid, issues = validate_bambara_text(text)
    
    return {
        'total_characters': len(text),
        'alphabetic_characters': len(chars),
        'word_count': len(words),
        'vowel_count': vowels,
        'consonant_count': consonants,
        'special_char_count': special,
        'tone_marks': tone_counts,
        'has_tone_marks': has_tone_marks(text),
        'contractions_found': contractions_found,
        'is_valid_orthography': is_valid,
        'orthography_issues': issues,
        'unique_characters': sorted(set(c for c in text if c.isalpha())),
    }


def create_pronunciation_key() -> Dict[str, str]:
    return {
        'a': '[a]',
        'b': '[b]',
        'c': '[tʃ]',
        'd': '[d]',
        'e': '[e]',
        'ɛ': '[ɛ]',
        'f': '[f]',
        'g': '[g]',
        'h': '[h]',
        'i': '[i]',
        'j': '[dʒ]',
        'k': '[k]',
        'l': '[l]',
        'm': '[m]',
        'n': '[n]',
        'ɲ': '[ɲ]',
        'ŋ': '[ŋ]',
        'o': '[o]',
        'ɔ': '[ɔ]',
        'p': '[p]',
        'r': '[r]',
        's': '[s]',
        't': '[t]',
        'u': '[u]',
        'w': '[w]',
        'y': '[j]',
        'z': '[z]',
    }


