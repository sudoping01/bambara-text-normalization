<h1 align="center">
    Bambara Text Normalizer
</h1>
<p align="center">
    <em>Text normalization for Bambara (Bamanankan)</em>
</p>
<p align="center">
    <a href="#installation">Installation</a> •
    <a href="#usage">Usage</a> •
    <a href="#linguistic-decisions">Linguistic Decisions</a> •
    <a href="#known-limitations">Limitations</a> •
    <a href="#evaluation-metrics">Metrics</a> •
    <a href="#references">References</a>
</p>

---

<p align="justify">
Text normalization broadly encompasses two related but distinct tasks in conversational AI pipelines:
</p>
<ul align="justify">
    <li><b>Text Normalization (TN)</b>: Converting written-form text to its verbalized/spoken form (e.g., "$123" → "one hundred twenty-three dollars"). Essential preprocessing for text-to-speech (TTS).</li>
    <li><b>Inverse Text Normalization (ITN)</b>: Converting spoken-form text to written form (the reverse). Used in ASR post-processing to improve readability and downstream task performance (e.g., machine translation, NER).</li>
</ul>
<p align="justify">
State-of-the-art systems (e.g., <a href="https://github.com/NVIDIA/NeMo">NVIDIA NeMo</a>) primarily address <b>semiotic classes</b>  tokens where spoken and written forms differ (dates, cardinals, measures, currency, etc.)  using WFST-based grammars, neural models, or hybrids. These support a growing set of languages (English, Spanish, German, French, Russian, Chinese, etc.) and allow grammar customization for new languages.
</p>
<p align="justify">
For low-resource languages like Bambara, however, the primary challenge in ASR evaluation is not semiotic classes but <b>orthographic variation</b>: the same spoken utterance can be validly transcribed in multiple ways (contracted <code>k'a ta</code> vs. expanded <code>ka a ta</code>, legacy <code>ny</code> vs. modern <code>ɲ</code>, with/without tone marks). Without normalization, WER/CER unfairly penalizes models for human writing inconsistencies rather than recognition errors.
</p>
<p align="justify">
This lightweight, rule-based tool provides linguistically-informed normalization tailored to these Bambara-specific issues, enabling fair ASR evaluation. It complements general-purpose TN/ITN systems by focusing on grammatical and orthographic variants rather than semiotic tokens.
</p>

---

## Installation
```bash
pip install git+https://github.com/sudoping01/bambara-text-normalization.git
```

## Usage

#### Basic Normalization
```python
from bambara_normalizer import BambaraNormalizer

normalizer = BambaraNormalizer()
normalizer("B'a fɔ")       # → "bɛ a fɔ"
normalizer("nyama bèlè")   # → "ɲama bɛlɛ"
normalizer("k'a ta")       # → "ka a ta"
normalizer("k'a la")       # → "kɛ a la"
```

#### ASR Evaluation
```python
from bambara_normalizer import BambaraEvaluator

evaluator = BambaraEvaluator()
result = evaluator.evaluate(reference="B'a fɔ", hypothesis="bɛ a fɔ")
print(f"WER: {result.wer:.2%}")
print(f"CER: {result.cer:.2%}")
```

#### Configuration Presets
```python
from bambara_normalizer import BambaraNormalizer, BambaraNormalizerConfig

# For WER evaluation (removes tones)
normalizer = BambaraNormalizer(BambaraNormalizerConfig.for_wer_evaluation())

# Preserve tone marks
normalizer = BambaraNormalizer(BambaraNormalizerConfig.preserving_tones())

# Minimal normalization
normalizer = BambaraNormalizer(BambaraNormalizerConfig.minimal())
```

#### Command Line
```bash
bambara-normalize "B'a fɔ́"
bambara-normalize --preset wer "N t'a don"
bambara-normalize --evaluate reference.txt hypothesis.txt
```

---

## Linguistic Decisions

### Why Normalize?

Bambara orthography allows variation. For the same spoken utterance:
- Annotator A writes: `k'a ta`
- Annotator B writes: `ka a ta`

**Both are correct.** You see both styles in published texts (stories, documents, datasets). Without normalization, we penalize the model for something that is not its fault  the inconsistency is in human writing conventions, not in speech recognition.

### Contraction Expansion

| Input | Output | Function |
|-------|--------|----------|
| `b'` | `bɛ` | Affirmative imperfective |
| `t'` | `tɛ` | Negative imperfective |
| `y'` | `ye` | Perfective marker |
| `n'` | `ni` | Conjunction |
| `k'` | `ka` / `kɛ` / `ko` | Context-dependent (see below) |

### k' Disambiguation

The contraction `k'` is highly ambiguous and can derive from **three** different sources:

| Source | Meaning | Example |
|--------|---------|---------|
| `ka` | Infinitive marker | `k'a ta` → `ka a ta` (to take it) |
| `kɛ` | Verb "to do/make" | `k'a la` → `kɛ a la` (do it there) |
| `ko` | Verb "to say" | `k'an ka` → `ko an ka` (said we should) |

**Disambiguation rules** (applied in priority order, derived from [Daba grammar](https://github.com/maslinych/daba) and corpus patterns):

1. **Benefactive construction**: `k' + pronoun + ma + X + ye` → `kɛ` ("be X for someone")  
   Example: `k'a ma hɛrɛ ye` → `kɛ a ma hɛrɛ ye` (be peace for him)

2. **Reported speech after `ma`**: `k' + pronoun + ma +` clause marker → `ko`  
   Example: `k'anw ma ko` → `ko anw ma ko` (said to us that...)

3. **Postpositional use**: `k' + pronoun +` postposition → `kɛ`  
   Postpositions: `la`, `na`, `ye`, `fɛ`, `kɔnɔ`, `kɔ`, `kɔrɔ`, `kan`, `kun`, `ɲɛ`, `bolo`, etc.

4. **Direct reported speech**: `k' + pronoun +` clause marker → `ko`  
   Clause markers: `ka`, `kana`, `bɛ`, `tɛ`, `bɛna`, `tɛna`, `tun`, `mana`, etc.

5. **Default**: `k' + pronoun +` verb/other → `ka` (infinitive marker)

#### Examples

| Input | Output | Reason |
|-------|--------|--------|
| `k'a la` | `kɛ a la` | `la` is postposition |
| `k'a fɛ` | `kɛ a fɛ` | `fɛ` is postposition |
| `k'a ma hɛrɛ ye` | `kɛ a ma hɛrɛ ye` | Benefactive (ma...ye pattern) |
| `k'a ma tasuma ye` | `kɛ a ma tasuma ye` | Benefactive (ma...ye pattern) |
| `k'anw ma ko` | `ko anw ma ko` | Reported speech marker after `ma` |
| `k'an kana` | `ko an kana` | Direct clause marker (`kana`) |
| `k'an ka ta` | `ko an ka ta` | Direct clause marker (`ka`) |
| `k'a ta` | `ka a ta` | Default (followed by verb `ta`) |
| `k'a fɔ` | `ka a fɔ` | Default (followed by verb `fɔ`) |

### Legacy Orthography

| Legacy | Modern | Notes |
|--------|--------|-------|
| `è` | `ɛ` | Pre-standard spelling |
| `ò` | `ɔ` | Pre-standard spelling |
| `ny` | `ɲ` | Digraph → single character |
| `ng` | `ŋ` | Digraph → single character |
| `ñ` | `ɲ` | Senegalese/Spanish variant |

---

## Known Limitations

### Inherent Linguistic Ambiguity

Some Bambara constructions are **genuinely ambiguous** and cannot be resolved without sentence-level or discourse-level context. This is not a limitation of the normalizer  it reflects real ambiguity in the language.

#### The `ye` Ambiguity

The word `ye` has multiple grammatical functions in Bambara:

| Function | POS | Example | Meaning |
|----------|-----|---------|---------|
| Postposition | pp | `à fɔ́ ń yé` | say it **to** me |
| Perfective auxiliary | pm | `ù ye ɲɔ̀ gòsi` | they **have** beaten the millet |
| Equative copula | cop | `ò yé kɔ̀nɔ yé` | it **is** a bird |
| Verb "to see" | v | `ka a ye` | **to see** it |
| Imperative plural | pm | `á' yé nà!` | come! (you all) |

This creates genuine ambiguity for `k'a ye`:

| Interpretation | Expansion | Meaning |
|----------------|-----------|---------|
| Postposition | `kɛ a ye` | do it for him |
| Verb "to see" | `ka a ye` | to see it |

**Both are grammatically valid.** Without broader context, the normalizer cannot determine which is intended.

#### Default Behavior

When faced with true ambiguity, the normalizer chooses the **statistically more frequent** interpretation based on corpus data:

| Ambiguous Input | Default Output | Reason |
|-----------------|----------------|--------|
| `k'a ye` | `kɛ a ye` | Postpositional `ye` is more frequent than verb `ye` |

#### Extended Ambiguous Cases

Even with more context, some sentences remain ambiguous:

```
Input:  k'a ye i ka so
```

| Interpretation 1 | Interpretation 2 |
|------------------|------------------|
| `kɛ a ye i ka so` | `ka a ye i ka so` |
| "do it for him at your house" | "to see him at your house" |

Both readings are syntactically valid. The normalizer defaults to `kɛ` (postpositional interpretation), but users should be aware that the verb interpretation exists.

<!-- ### Scope of Disambiguation

The normalizer uses **local context** (1-3 word lookahead) for disambiguation. It does not:

- Parse full sentence structure
- Use a dictionary/lexicon for POS tagging
- Consider discourse-level context
- Handle rare or dialectal constructions

For applications requiring higher accuracy on ambiguous cases, consider:
- Using the [Daba morphological analyzer](https://github.com/maslinych/daba) with full dictionary lookup
- Manual review of edge cases
- Training a neural disambiguation model on annotated data -->

### What This Means for ASR Evaluation

For ASR evaluation purposes, these ambiguities are generally **acceptable** because:

1. Both expansions represent valid transcriptions of the same spoken input
2. The normalizer applies the same default consistently to both reference and hypothesis
3. True recognition errors (wrong words entirely) will still be caught

The goal is **fair comparison**, not perfect linguistic analysis.

---

## Evaluation Metrics

| Metric | Description |
|--------|-------------|
| **WER** | Word Error Rate |
| **CER** | Character Error Rate |
| **MER** | Match Error Rate |
| **WIL** | Word Information Lost |
| **DER** | Diacritic Error Rate (tone accuracy) |

---

## Running Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

Current test coverage: **78 tests passing** (2 skipped for edge cases requiring manual verification).

---

## References

#### Linguistic Resources
- [Bambara Reference Corpus](http://cormand.huma-num.fr/)  Primary corpus for Bambara
- [Daba Morphological Analyzer](https://github.com/maslinych/daba)  Grammar rules for disambiguation
- [Bamadaba Dictionary](http://cormand.huma-num.fr/bamadaba.html)  Bambara lexical database
- DNAFLA / AMALAN  Bambara standardization body

#### Standards
- UNESCO Bamako Meeting (1966)
- Niamey African Reference Alphabet (1978)

#### Tools
- [jiwer](https://github.com/jitsi/jiwer)  ASR evaluation metrics

#### Related Work & Broader TN/ITN
- [Text Normalization and Inverse Text Normalization with NVIDIA NeMo](https://developer.nvidia.com/blog/text-normalization-and-inverse-text-normalization-with-nvidia-nemo/)
- [NeMo Text Normalization Documentation](https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/stable/nlp/text_normalization/wfst/wfst_text_normalization.html)
- [NeMo Grammar Customization Guide](https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/stable/nlp/text_normalization/wfst/wfst_customization.html)
- [NVIDIA NeMo Repository](https://github.com/NVIDIA/NeMo)

---

## License

MIT License  see [LICENSE](LICENSE) for details.

---

<p align="center">
    <a href="https://github.com/MALIBA-AI">MALIBA-AI</a>
</p>