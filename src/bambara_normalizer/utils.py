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

# =======================#
# BAMBARA CHARACTER SETS #
# =======================#

BAMBARA_VOWELS = set("aeiouɛɔ")
BAMBARA_VOWELS_UPPER = set("AEIOUƐƆ")
BAMBARA_CONSONANTS = set("bcdfghjklmnprstwyzɲŋ")
BAMBARA_CONSONANTS_UPPER = set("BCDFGHJKLMNPRSTWYZƝŊ")
BAMBARA_SPECIAL_CHARS = set("ɛɔɲŋƐƆƝŊ")
BAMBARA_NASAL_VOWELS = {"an", "en", "ɛn", "in", "on", "ɔn", "un"}
BAMBARA_ALPHABET = set("abcdefghijklmnoprstuwyzɛɔɲŋ")

# ===========#
# TONE MARKS #
# ===========#

TONE_MARKS = {
    "\u0300": "low",  # grave accent
    "\u0301": "high",  # acute accent
    "\u030c": "rising",  # caron
    "\u0302": "falling",  # circumflex
    "\u0304": "mid",  # macron
}

# =====================#
# CONTRACTION MAPPINGS #
# =====================#

CONTRACTION_MAP = {
    "bɛ": "b'",
    "tɛ": "t'",
    "ye": "y'",
    "ni": "n'",
    "na": "n'",
    "ka": "k'",
    "kɛ": "k'",
    "ko": "k'",
    "ma": "m'",
    "sa": "s'",
}

EXPANSION_MAP = {
    "b'": ["bɛ"],
    "t'": ["tɛ"],
    "y'": ["ye"],
    "n'": ["ni", "na"],  # Ambiguous
    "k'": ["ka", "kɛ", "ko"],  # Ambiguous
    "m'": ["ma"],
    "s'": ["sa"],
}


# ====================#
# CHARACTER FUNCTIONS #
# ====================#


def is_bambara_char(char: str) -> bool:
    base_char = get_base_char(char.lower())
    return base_char in BAMBARA_ALPHABET


def is_bambara_special_char(char: str) -> bool:
    return char in BAMBARA_SPECIAL_CHARS


def is_bambara_vowel(char: str) -> bool:
    base_char = get_base_char(char.lower())
    return base_char in BAMBARA_VOWELS


def is_bambara_consonant(char: str) -> bool:
    base_char = get_base_char(char.lower())
    return base_char in BAMBARA_CONSONANTS


def get_base_char(char: str) -> str:
    decomposed = unicodedata.normalize("NFD", char)
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


# =============================================================================
# TONE FUNCTIONS
# =============================================================================


def get_tone(char: str) -> str | None:
    """
    Get the tone of a character, if any.

    Args:
        char: Single character (possibly with diacritic)

    Returns:
        Tone name ('low', 'high', 'rising', 'falling', 'mid') or None
    """
    decomposed = unicodedata.normalize("NFD", char)
    for c in decomposed:
        if c in TONE_MARKS:
            return TONE_MARKS[c]
    return None


def add_tone(char: str, tone: str) -> str:
    """
    Add a tone mark to a character.

    Args:
        char: Base character
        tone: Tone name ('low', 'high', 'rising', 'falling', 'mid')

    Returns:
        Character with tone mark

    Raises:
        ValueError: If tone is not recognized
    """
    tone_to_mark = {v: k for k, v in TONE_MARKS.items()}
    if tone not in tone_to_mark:
        raise ValueError(f"Unknown tone: {tone}. Valid: {list(TONE_MARKS.values())}")

    base = get_base_char(char)
    return unicodedata.normalize("NFC", base + tone_to_mark[tone])


def remove_tones(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    result = "".join(c for c in decomposed if c not in TONE_MARKS)
    return unicodedata.normalize("NFC", result)


def has_tone_marks(text: str) -> bool:
    decomposed = unicodedata.normalize("NFD", text)
    return any(c in TONE_MARKS for c in decomposed)


def count_tone_marks(text: str) -> dict[str, int]:
    """
    Count tone marks by type in text.

    Returns:
        Dictionary with tone names as keys and counts as values
    """
    decomposed = unicodedata.normalize("NFD", text)
    counts = dict.fromkeys(TONE_MARKS.values(), 0)
    for c in decomposed:
        if c in TONE_MARKS:
            counts[TONE_MARKS[c]] += 1
    return counts


# ======================#
# CONTRACTION FUNCTIONS #
# ======================#


def is_contraction(word: str) -> bool:
    """
    Check if a word is a Bambara contraction.

    Args:
        word: Word to check

    Returns:
        True if word contains a contraction pattern
    """
    word_lower = word.lower()
    for prefix in EXPANSION_MAP.keys():
        if prefix in word_lower:
            return True
    return False


def get_contraction_type(word: str) -> str | None:
    """
    Get the contraction prefix type if word is a contraction.

    Args:
        word: Word to check

    Returns:
        Contraction prefix (e.g., "b'", "k'") or None
    """
    word_lower = word.lower()
    for prefix in EXPANSION_MAP.keys():
        if word_lower.startswith(prefix):
            return prefix
    return None


def get_possible_expansions(contraction: str) -> list[str]:
    """
    Get possible expansions for a contraction prefix.

    Args:
        contraction: Contraction prefix (e.g., "k'")

    Returns:
        List of possible expanded forms

    Example:
        >>> get_possible_expansions("k'")
        ['ka', 'kɛ', 'ko']
    """
    return EXPANSION_MAP.get(contraction.lower(), [])


def can_contract(word: str) -> bool:
    """
    Check if a word can be contracted.

    Args:
        word: Word to check

    Returns:
        True if word is in CONTRACTION_MAP
    """
    return word.lower() in CONTRACTION_MAP


def get_contracted_form(word: str) -> str | None:
    """
    Get the contracted form of a word.

    Args:
        word: Expanded form (e.g., "bɛ")

    Returns:
        Contracted prefix (e.g., "b'") or None
    """
    return CONTRACTION_MAP.get(word.lower())


def find_contractions(text: str) -> list[str]:
    """
    Find all contractions in text.

    Args:
        text: Text to search

    Returns:
        List of contraction patterns found
    """
    found = []
    text_lower = text.lower()
    for prefix in EXPANSION_MAP.keys():
        if prefix in text_lower:
            found.append(prefix)
    return found


def find_contractable_sequences(text: str) -> list[tuple[str, str]]:
    """
    Find word pairs that can be contracted.

    Args:
        text: Text to search

    Returns:
        List of (expanded_word, next_word) tuples that can be contracted

    Example:
        >>> find_contractable_sequences("bɛ a fɔ")
        [('bɛ', 'a')]
    """
    words = text.split()
    contractable = []

    for i, word in enumerate(words[:-1]):
        word_lower = word.lower()
        next_word = words[i + 1].lower()

        if word_lower in CONTRACTION_MAP:
            if next_word and next_word[0] in BAMBARA_VOWELS:
                contractable.append((word, words[i + 1]))

    return contractable


# ===================#
# SYLLABLE FUNCTIONS #
# ===================#


def is_nasal_vowel(chars: str) -> bool:
    if len(chars) != 2:
        return False
    return chars.lower() in BAMBARA_NASAL_VOWELS


def split_syllables(word: str) -> list[str]:
    """
    Basic syllable splitting for Bambara words.

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
                digraph = word[i : i + 2]
                if digraph in ("ny", "ng", "sh", "kh", "gb", "gw"):
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
                elif next_char == "n" and (i + 2 >= len(word) or word[i + 2] not in BAMBARA_VOWELS):
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


# =====================#
# VALIDATION FUNCTIONS #
# =====================#


def validate_bambara_text(text: str) -> tuple[bool, list[str]]:
    """
    Validate text for Bambara orthographic compliance.

    Args:
        text: Text to validate

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []

    for i, char in enumerate(text):
        if char.isalpha() and not is_bambara_char(char):
            if char not in "qvxQVX":
                issues.append(f"Non-Bambara character '{char}' at position {i}")

    legacy_patterns = [
        ("ny", "Should use ɲ instead of ny"),
        ("ng", "Should use ŋ instead of ng (unless in compound)"),
        ("è", "Should use ɛ instead of è"),
        ("ò", "Should use ɔ instead of ò"),
    ]
    text_lower = text.lower()
    for pattern, message in legacy_patterns:
        if pattern in text_lower:
            issues.append(message)

    return len(issues) == 0, issues


def normalize_unicode_variants(text: str) -> str:
    """
    Normalize visually similar but differently encoded characters.

    Handles common Unicode confusion issues with Bambara special characters.

    Args:
        text: Text to normalize

    Returns:
        Text with normalized characters
    """
    char_map = {
        "ε": "ɛ",  # Greek epsilon
        "Ε": "Ɛ",  # Greek capital epsilon
        "є": "ɛ",  # Cyrillic ie
        "Є": "Ɛ",  # Cyrillic capital ie
        "э": "ɛ",  # Cyrillic e
        "Э": "Ɛ",  # Cyrillic capital e
        "ᴐ": "ɔ",  # Small capital o
        "ɳ": "ŋ",  # Retroflex n (wrong)
        "ñ": "ɲ",  # Spanish ñ
        "Ñ": "Ɲ",
    }

    return "".join(char_map.get(c, c) for c in text)


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================


def get_unicode_info(char: str) -> dict[str, str]:
    """
    Get Unicode information for a character.

    Args:
        char: Single character

    Returns:
        Dictionary with Unicode information
    """
    if len(char) != 1:
        char = char[0]

    return {
        "character": char,
        "codepoint": f"U+{ord(char):04X}",
        "name": unicodedata.name(char, "UNKNOWN"),
        "category": unicodedata.category(char),
        "decomposition": unicodedata.decomposition(char) or "None",
    }


def analyze_text(text: str) -> dict:
    """
    Analyze Bambara text for various properties.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with analysis results including:
        - Character counts (total, alphabetic, vowels, consonants)
        - Word count
        - Tone mark information
        - Contractions found
        - Orthography validation
    """
    chars = [c for c in text if c.isalpha()]
    words = text.split()

    vowels = sum(1 for c in chars if c.lower() in BAMBARA_VOWELS)
    consonants = sum(1 for c in chars if c.lower() in BAMBARA_CONSONANTS)
    special = sum(1 for c in chars if is_bambara_special_char(c))

    tone_counts = count_tone_marks(text)
    contractions_found = find_contractions(text)
    contractable = find_contractable_sequences(text)

    is_valid, issues = validate_bambara_text(text)

    return {
        "total_characters": len(text),
        "alphabetic_characters": len(chars),
        "word_count": len(words),
        "vowel_count": vowels,
        "consonant_count": consonants,
        "special_char_count": special,
        "tone_marks": tone_counts,
        "has_tone_marks": has_tone_marks(text),
        "contractions_found": contractions_found,
        "contractable_sequences": contractable,
        "is_valid_orthography": is_valid,
        "orthography_issues": issues,
        "unique_characters": sorted({c for c in text if c.isalpha()}),
    }


def create_pronunciation_key() -> dict[str, str]:
    """
    Create a pronunciation key for Bambara characters.

    Returns:
        Dictionary mapping characters to IPA pronunciations
    """
    return {
        "a": "[a]",
        "b": "[b]",
        "c": "[tʃ]",
        "d": "[d]",
        "e": "[e]",
        "ɛ": "[ɛ]",
        "f": "[f]",
        "g": "[g]",
        "h": "[h]",
        "i": "[i]",
        "j": "[dʒ]",
        "k": "[k]",
        "l": "[l]",
        "m": "[m]",
        "n": "[n]",
        "ɲ": "[ɲ]",
        "ŋ": "[ŋ]",
        "o": "[o]",
        "ɔ": "[ɔ]",
        "p": "[p]",
        "r": "[r]",
        "s": "[s]",
        "t": "[t]",
        "u": "[u]",
        "w": "[w]",
        "y": "[j]",
        "z": "[z]",
    }


def compare_normalization_modes(text: str) -> dict[str, str]:
    """
    Compare the output of different normalization modes on the same text.

    Useful for debugging and understanding how modes differ.

    Args:
        text: Text to normalize

    Returns:
        Dictionary with mode names as keys and normalized text as values
    """
    from .normalizer import BambaraNormalizer, BambaraNormalizerConfig

    results = {"original": text}

    for mode in ["expand", "contract", "preserve"]:
        config = BambaraNormalizerConfig(contraction_mode=mode)
        normalizer = BambaraNormalizer(config)
        results[mode] = normalizer(text)

    return results
