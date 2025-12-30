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
    <a href="#evaluation-metrics">Metrics</a> •
    <a href="#references">References</a>
</p>

---

<p align="justify">
ASR evaluation for Bambara faces a fundamental challenge: <b>orthographic variation</b>. The same spoken utterance can be written multiple ways contracted (<code>k'a ta</code>) or expanded (<code>ka a ta</code>), with legacy orthography (<code>ny</code>) or modern standard (<code>ɲ</code>), with or without tone marks. These are not transcription errors but valid writing conventions.
</p>

<p align="justify">
Without normalization, WER metrics <b>penalize models for human inconsistency</b>, not actual recognition errors. This tool provides linguistically-informed text preprocessing for fair ASR evaluation, built on <a href="https://github.com/jitsi/jiwer">jiwer</a>.
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
normalizer("B'a fɔ")      # → "bɛ a fɔ"
normalizer("nyama bèlè")  # → "ɲama bɛlɛ"
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

Bambara orthography allows variation. For the same spoken speech:
- Annotator A writes: `k'a ta`
- Annotator B writes: `ka a ta`

**Both are correct.** You see both styles in published texts (stories, documents, datasets ...). Without normalization, we penalize the model for something that is not its fault, the inconsistency is in human writing conventions, not in speech recognition.

### Contraction Expansion

| Input | Output | Function |
|-------|--------|----------|
| `b'` | `bɛ` | Affirmative imperfective |
| `t'` | `tɛ` | Negative imperfective |
| `y'` | `ye` | Perfective marker |
| `n'` | `ni` | Conjunction |
| `k'` | `ka` / `kɛ` | Context-dependent (see below) |

### k' Disambiguation

The contraction `k'` is ambiguous it can derive from two sources:

| Source | Meaning | Example |
|--------|---------|---------|
| `ka` | Infinitive marker | `k'a ta` → `ka a ta` |
| `kɛ` | Verb "to do/make" | `k'a la` → `kɛ a la` |

**Disambiguation rule** (derived from [Daba grammar](https://github.com/maslinych/daba)):
```
k' + vowel + POSTPOSITION  →  kɛ (verb)
k' + vowel + VERB/OTHER    →  ka (infinitive, default)
```

Postpositions form a **closed class** in Bambara (~20 words: `la`, `ma`, `ye`, `fɛ`, `kɔnɔ`, etc.), making rule-based disambiguation feasible. Verbs are an open class and cannot be exhaustively listed.

| Input | Output | Reason |
|-------|--------|--------|
| `k'a la` | `kɛ a la` | `la` is postposition |
| `k'a ma` | `kɛ a ma` | `ma` is postposition |
| `k'a ta` | `ka a ta` | `ta` is verb |
| `k'a fɔ` | `ka a fɔ` | `fɔ` is verb |

### Legacy Orthography

| Legacy | Modern | Notes |
|--------|--------|-------|
| `è` | `ɛ` | Pre-standard spelling |
| `ò` | `ɔ` | Pre-standard spelling |
| `ny` | `ɲ` | Digraph → single character |
| `ng` | `ŋ` | Digraph → single character |
| `ñ` | `ɲ` | Senegalese variant |

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

---

## References

#### Linguistic Resources
- [Bambara Reference Corpus](http://cormand.huma-num.fr/)  Primary corpus for Bambara
- [Daba Morphological Analyzer](https://github.com/maslinych/daba)  Grammar rules for disambiguation
- DNAFLA / AMALAN  Bambara standardization body

#### Standards
- UNESCO Bamako Meeting (1966)
- Niamey African Reference Alphabet (1978)

#### Tools
- [jiwer](https://github.com/jitsi/jiwer)  ASR evaluation metrics

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
    <a href="https://github.com/MALIBA-AI">MALIBA-AI</a>
</p>