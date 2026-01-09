<h1 align="center">
    Bambara Text Normalizer
</h1>
<p align="center">
    <em>Text Normalization & ASR Evaluation Framework for Bambara (Bamanankan)</em>
</p>
<p align="center">
    <a href="#installation">Installation</a> •
    <a href="#text-normalization">Normalization</a> •
    <a href="#asr-evaluation-framework">ASR Evaluation</a> •
    <a href="#contraction-modes">Modes</a> •
    <a href="#command-line-interface">CLI</a> •
    <a href="#linguistic-decisions">Linguistics</a> •
    <a href="#references">References</a>
</p>

---

## Purpose

This tool serves **two complementary purposes** for Bambara language processing:

| Purpose | Description |
|---------|-------------|
| **Text Normalization** | Standardize Bambara text for any downstream NLP task (TTS, MT, NER, etc.) |
| **ASR Evaluation** | Fair WER/CER computation that accounts for valid orthographic variation |

> [!NOTE]
> Bambara orthography allows variation: the same utterance can be written as `k'a ta` or `ka a ta`  both are correct. Without normalization, evaluation metrics unfairly penalize models for human writing inconsistencies rather than actual recognition errors.

---

## Installation

```bash
pip install git+https://github.com/sudoping01/bambara-text-normalization.git
```

---

## Text Normalization




```python
from bambara_normalizer import normalize

# Default: expand contractions
normalize("⁠Ne k’a ma ko ayi")           
normalize("⁠K’ale t’a fɛ k’a kɛ")    
normalize("⁠K’i k’i janto i yɛrɛ la")        


# Contract mode: collapse expanded forms
normalize("Ne ko a ma ko ayi", mode="contract")    
normalize("Ko ale tɛ a fɛ ka o kɛ", mode="contract")    
normalize("Ko i ka i janto i yɛrɛ la", mode="contract")    

# Preserve mode: don't touch contractions
normalize("K’i k’i janto i yɛrɛ la", mode="preserve")     
```

### Custom Settings

```python
from bambara_normalizer import normalize

# Full control over normalization
text = normalize(
    "Ka na son k’o k’a la",
    mode="expand",                      # "expand" | "contract" | "preserve"
    preserve_tones=False,               
    normalize_legacy_orthography=True, 
    lowercase=True,                     
    remove_punctuation=False,           
    normalize_whitespace=True,         
    normalize_apostrophes=True,         
    normalize_special_chars=True,     
    expand_numbers=False,             
    remove_diacritics_except_tones=False,  
    handle_french_loanwords=True,   
    strip_repetitions=False,       
    normalize_compounds=True, 
)
```

### Using BambaraNormalizer Class

For repeated normalization with consistent settings:

```python
from bambara_normalizer import BambaraNormalizer, BambaraNormalizerConfig


config = BambaraNormalizerConfig(contraction_mode="expand") # change it to "contract" or preserve
normalizer = BambaraNormalizer(config)
normalizer("A y'a fɔ")      
normalizer("k'a la")   

# Contraction mode
config = BambaraNormalizerConfig(contraction_mode="contract")
normalizer = BambaraNormalizer(config)
normalizer("bɛ a fɔ")     
normalizer("ka a ta")     
```

### Predefined Configuration Presets

```python
from bambara_normalizer import BambaraNormalizer, BambaraNormalizerConfig

# For WER evaluation (aggressive normalization, removes tones)
normalizer = BambaraNormalizer(BambaraNormalizerConfig.for_wer_evaluation())

# For WER with contract mode
normalizer = BambaraNormalizer(BambaraNormalizerConfig.for_wer_evaluation(mode="contract"))

# For CER evaluation
normalizer = BambaraNormalizer(BambaraNormalizerConfig.for_cer_evaluation())

# Preserve tone marks
normalizer = BambaraNormalizer(BambaraNormalizerConfig.preserving_tones())

# Minimal normalization (only essential fixes)
normalizer = BambaraNormalizer(BambaraNormalizerConfig.minimal())
```

---

## ASR Evaluation Framework

### Quick Evaluation

```python
from bambara_normalizer import evaluate


result = evaluate(
    reference="B'a fɔ ka taa",
    hypothesis="bɛ a fɔ ka taa"

)


print(f"WER: {result.wer:.2%}")  
print(f"CER: {result.cer:.2%}")
print(f"MER: {result.mer:.2%}")
```

### Evaluator with Mode Selection

> [!IMPORTANT]
> The `mode` parameter determines how contractions are handled during evaluation. This significantly impacts WER scores when reference and hypothesis use different orthographic conventions.

```python
from bambara_normalizer import evaluate


result = evaluate(
    reference="k'a ta", 
    hypothesis="ka a ta"
    mode="expand" # contract | preserve 
    )
print(f"WER: {result.wer:.2%}")   
```

### Flexible Configuration

For full control use the evalution class and define the normalization configuration:

```python
from bambara_normalizer import (
    BambaraNormalizer, 
    BambaraNormalizerConfig, 
    BambaraEvaluator
)

# Define custom normalizer: same then the config we did upside
config = BambaraNormalizerConfig(
    contraction_mode="contract",
    preserve_tones=False,
    lowercase=True,
    remove_punctuation=True,
    normalize_legacy_orthography=True,
)


evaluator = BambaraEvaluator(config=config)


result = evaluator.evaluate(
    reference="K'a fɔ́!",
    hypothesis="ka a fo"
)
print(f"WER: {result.wer:.2%}")
```

### Batch Evaluation

```python
from bambara_normalizer import BambaraEvaluator

evaluator = BambaraEvaluator(mode="contract")

references = ["k'a ta", "b'a fɔ", "n'a ma"]
hypotheses = ["ka a ta", "bɛ a fɔ", "na a ma"]

aggregate, individual = evaluator.evaluate_batch(references, hypotheses)

print(f"Overall WER: {aggregate.wer:.2%}")
for i, result in enumerate(individual):
    print(f"  [{i}] WER: {result.wer:.2%}")
```

### Available Metrics

| Metric | Method | Description |
|--------|--------|-------------|
| **WER** | `evaluator.wer(ref, hyp)` | Word Error Rate |
| **CER** | `evaluator.cer(ref, hyp)` | Character Error Rate |
| **MER** | `evaluator.mer(ref, hyp)` | Match Error Rate |
| **WIL** | `evaluator.wil(ref, hyp)` | Word Information Lost |
| **WIP** | `evaluator.wip(ref, hyp)` | Word Information Preserved |
| **DER** | `result.der` | Diacritic Error Rate (tone accuracy) |

---

## Contraction Modes

> [!WARNING]
> Choosing the right mode is critical for fair ASR evaluation. Using the wrong mode can inflate or deflate WER scores artificially.

Version 2.0 introduces **three contraction modes** to handle bidirectional Bambara orthography:

| Mode | Direction | When to Use |
|------|-----------|-------------|
| `expand` | `b'a` → `bɛ a` | Default. Full linguistic analysis with k'/n' disambiguation |
| `contract` | `bɛ a` → `b'a` | Simpler, more forgiving. No disambiguation ambiguity |
| `preserve` | No change | Debugging, or when you want raw comparison |

### Why Contract Mode Matters

**Expansion is complex**  the contraction `k'` can expand to three different words:

| Contraction | Possible Expansions | Meaning |
|-------------|---------------------|---------|
| `k'a` | `ka a` | infinitive marker |
| `k'a` | `kɛ a` | verb "to do" |
| `k'a` | `ko a` | verb "to say" |

The normalizer uses context to disambiguate, but some cases are genuinely ambiguous.

**Contraction is simple**  all variants collapse to the same form:

```
ka a  ─┐
kɛ a  ─┼─>  k'a
ko a  ─┘
```

> [!TIP]
> For ASR evaluation, **contract mode is more forgiving** because it doesn't penalize the model for disambiguation differences when both forms are linguistically valid.

### Contraction Mappings

| Expanded | Contracted | Function |
|----------|------------|----------|
| `bɛ` + vowel | `b'` | Affirmative imperfective |
| `tɛ` + vowel | `t'` | Negative imperfective |
| `ye` + vowel | `y'` | Perfective marker |
| `ni` + vowel | `n'` | Conjunction |
| `na` + vowel | `n'` | Verb "come" |
| `ka` + vowel | `k'` | Infinitive marker |
| `kɛ` + vowel | `k'` | Verb "to do" |
| `ko` + vowel | `k'` | Verb "to say" |

---

## Command Line Interface

### Basic Usage

```bash

# default mode is expand1
bambara-normalize "B'a fɔ́"
# Output: bɛ a fɔ

# Contract mode
bambara-normalize --mode contract "bɛ a fɔ"
# Output: b'a fɔ

# Preserve mode
bambara-normalize --mode preserve "B'a fɔ"
# Output: b'a fɔ
```

### With Presets

```bash
# WER preset (aggressive normalization)
bambara-normalize --preset wer "K'a fɔ́!"
# Output: ka a fɔ

# WER preset with contract mode
bambara-normalize --preset wer --mode contract "Ka a fɔ"
# Output: k'a fɔ

# CER preset
bambara-normalize --preset cer "B'a fɔ"
```

### File Evaluation

```bash
# Evaluate reference vs hypothesis files
bambara-normalize --evaluate reference.txt hypothesis.txt

# With contract mode
bambara-normalize --evaluate --mode contract ref.txt hyp.txt

# Output detailed metrics
bambara-normalize --evaluate --detailed ref.txt hyp.txt
```

### Batch Processing

```bash
# Process file line by line
bambara-normalize --input corpus.txt --output normalized.txt

# With specific mode
bambara-normalize --input corpus.txt --output normalized.txt --mode contract
```

---

## Linguistic Decisions

### Why Normalize?

Bambara orthography allows variation. For the same spoken utterance:
- Annotator A writes: `k'a ta`
- Annotator B writes: `ka a ta`

**Both are correct.** Without normalization, we penalize models for human writing inconsistencies, not recognition errors.

### n' Disambiguation

| Pattern | Expansion | Meaning |
|---------|-----------|---------|
| `n' + pronoun + ma` | `na` | Verb "to come" |
| `n' + other` | `ni` | Conjunction (default) |

**Examples:**
- `n'a ma` → `na a ma` (come to him)
- `n'a ta` → `ni a ta` (if he takes)

### k' Disambiguation Rules

Applied in priority order (derived from [Daba grammar](https://github.com/maslinych/daba)):

| Priority | Pattern | Result | Example |
|----------|---------|--------|---------|
| 1 | `k' + pronoun + ma + X + ye` | `kɛ` | `k'a ma hɛrɛ ye` → `kɛ a ma hɛrɛ ye` |
| 2 | `k' + pronoun + ma +` speech marker | `ko` | `k'anw ma ko` → `ko anw ma ko` |
| 3 | `k' + pronoun +` postposition | `kɛ` | `k'a la` → `kɛ a la` |
| 4 | `k' + pronoun +` clause marker | `ko` | `k'an ka ta` → `ko an ka ta` |
| 5 | Default | `ka` | `k'a ta` → `ka a ta` |

**Postpositions:** `la`, `na`, `ye`, `fɛ`, `kɔnɔ`, `kɔ`, `kɔrɔ`, `kan`, `kun`, `ɲɛ`, `bolo`

**Clause markers:** `ka`, `kana`, `bɛ`, `tɛ`, `bɛna`, `tɛna`, `tun`, `mana`

### Legacy Orthography Conversion

| Legacy | Modern | Notes |
|--------|--------|-------|
| `è` | `ɛ` | Pre-standard spelling |
| `ò` | `ɔ` | Pre-standard spelling |
| `ny` | `ɲ` | Digraph → single character |
| `ng` | `ŋ` | Digraph → single character |
| `ñ` | `ɲ` | Spanish/Senegalese variant |

---

## Known Limitations

### Inherent Linguistic Ambiguity

> [!CAUTION]
> Some Bambara constructions are **genuinely ambiguous** and cannot be resolved without broader context. This is not a bug  it reflects real ambiguity in the language.

#### The `ye` Problem

The word `ye` has **five** grammatical functions:

| Function | Example | Meaning |
|----------|---------|---------|
| Postposition | `à fɔ́ ń yé` | say it **to** me |
| Perfective | `ù ye ɲɔ̀ gòsi` | they **have** beaten |
| Copula | `ò yé kɔ̀nɔ yé` | it **is** a bird |
| Verb "see" | `ka a ye` | **to see** it |
| Imperative | `á' yé nà!` | come! (plural) |

This creates genuine ambiguity for `k'a ye`:

| Interpretation | Expansion | Meaning |
|----------------|-----------|---------|
| Postposition | `kɛ a ye` | do it for him |
| Verb "see" | `ka a ye` | to see it |

**Default behavior:** The normalizer chooses `kɛ a ye` (postposition is more frequent).

**Solution:** Use `mode="contract"` for ASR evaluation to avoid disambiguation penalties:

```python
evaluator = BambaraEvaluator(mode="contract")
# Both "kɛ a ye" and "ka a ye" => "k'a ye" 
```

### Scope

The normalizer uses **local context** (1-3 word lookahead). It does not:
- Parse full sentence structure
- Use dictionary/lexicon for POS tagging
- Consider discourse-level context

---

## Utility Functions

```python
from bambara_normalizer.utilities import (
    is_contraction,
    can_contract,
    find_contractions,
    find_contractable_sequences,
    compare_normalization_modes,
    analyze_text,
    is_bambara_vowel,
    get_tone,
    remove_tones,
)


is_contraction("b'a")                   
is_contraction("bɛ")                     
can_contract("bɛ a")                      

# Find patterns in text
find_contractions("B'a fɔ k'a ta")       # ["b'", "k'"]
find_contractable_sequences("bɛ a fɔ")   # [('bɛ', 'a')]

# Compare modes side-by-side
compare_normalization_modes("b'a fɔ")
# {'original': "b'a fɔ", 'expand': 'bɛ a fɔ', 'contract': "b'a fɔ", 'preserve': "b'a fɔ"}

# Full text analysis
analyze_text("B'a fɔ k'a la")
# {'word_count': 4, 'contractions_found': ["b'", "k'"], 'has_tone_marks': False, ...}

# Tone handling
get_tone("fɔ́")                           # "high"
remove_tones("fɔ́ bɛ̀")                    # "fɔ bɛ"
```

---

## Evaluation Metrics

| Metric | Description | Range |
|--------|-------------|-------|
| **WER** | Word Error Rate | 0.0 – ∞ |
| **CER** | Character Error Rate | 0.0 – ∞ |
| **MER** | Match Error Rate | 0.0 – 1.0 |
| **WIL** | Word Information Lost | 0.0 – 1.0 |
| **WIP** | Word Information Preserved | 0.0 – 1.0 |
| **DER** | Diacritic Error Rate (tone accuracy) | 0.0 – ∞ |

---



## References

#### Linguistic Resources
- [Bambara Reference Corpus](http://cormand.huma-num.fr/)  Primary corpus
- [Daba Morphological Analyzer](https://github.com/maslinych/daba)  Grammar rules
- [Bamadaba Dictionary](http://cormand.huma-num.fr/bamadaba.html)  Lexical database
- DNAFLA / AMALAN  Bambara standardization body

#### Standards
- UNESCO Bamako Meeting (1966)
- Niamey African Reference Alphabet (1978)

#### Tools
- [jiwer](https://github.com/jitsi/jiwer)  ASR evaluation metrics

#### Related Work
- [NVIDIA NeMo Text Normalization](https://github.com/NVIDIA/NeMo)
- [NeMo TN/ITN Documentation](https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/stable/nlp/text_normalization/wfst/wfst_text_normalization.html)

---

<p align="center">
    <a href="https://github.com/MALIBA-AI">MALIBA-AI</a>
</p>