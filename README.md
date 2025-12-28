# Bambara Text Normalizer

Text normalization tools for Bambara (Bamanankan) designed for ASR evaluation. Handles contractions, special characters, tone marks, and orthographic variations that affect WER/CER calculations.

## Project Description

ASR systems for Bambara face evaluation challenges due to orthographic inconsistencies between reference transcriptions and model outputs. Common issues include:

- Contracted forms (`b'a`) vs expanded forms (`bɛ a`)
- Legacy orthography (`ny`, `è`) vs modern standard (`ɲ`, `ɛ`)
- Inconsistent tone marking
- Apostrophe encoding variants

This normalizer provides consistent text preprocessing for fair WER/CER evaluation, along with evaluation utilities built on [jiwer](https://github.com/jitsi/jiwer).

## Installation
```bash
# NOT PUSHED ON PIPY YET (COMMING SOON)
pip install bambara-normalizer
```

Or from source:
```bash
git clone https://github.com/MALIBA-AI/bambara-normalizer.git
cd bambara-normalizer
pip install -e .
```

## Usage

### Text Normalization
```python
from bambara_normalizer import BambaraNormalizer

normalizer = BambaraNormalizer()
normalizer("B'a fɔ́")      # "bɛ a fɔ́"
normalizer("nyama bèlè")  # "ɲama bɛlɛ"
```

### ASR Evaluation
```python
from bambara_normalizer import BambaraEvaluator

evaluator = BambaraEvaluator()
result = evaluator.evaluate(reference="B'a fɔ́", hypothesis="bɛ a fɔ")

print(f"WER: {result.wer:.2%}")
print(f"CER: {result.cer:.2%}")
```

### Batch Evaluation
```python
references = ["B'a fɔ́", "n tɛ a lon", "a yé a fɔ"]
hypotheses = ["bɛ a fɔ", "n tɛ a lon", "a ye a fɔ"]

aggregate, individual = evaluator.evaluate_batch(references, hypotheses)
```

### Configuration

The normalizer supports different presets depending on your use case:
```python
from bambara_normalizer import BambaraNormalizer, BambaraNormalizerConfig

# Aggressive normalization for WER (removes tones)
normalizer = BambaraNormalizer(BambaraNormalizerConfig.for_wer_evaluation())

# Preserve tone marks
normalizer = BambaraNormalizer(BambaraNormalizerConfig.preserving_tones())

# Minimal normalization
normalizer = BambaraNormalizer(BambaraNormalizerConfig.minimal())
```

### Command Line
```bash
bambara-normalize "B'a fɔ́"
bambara-normalize --preset wer "Ń t'à lɔ̀n"
bambara-normalize --evaluate reference.txt hypothesis.txt
```

## Normalization Rules

### Contractions

| Input | Output | Function |
|-------|--------|----------|
| `b'` | `bɛ` | Affirmative imperfective |
| `t'` | `tɛ` | Negative imperfective |
| `y'` | `yé` | Perfective marker |
| `n'` | `ni` | Conjunction |
| `k'` | `ka` | Infinitive/subjunctive |

### Orthography

| Legacy | Modern |
|--------|--------|
| `è` | `ɛ` |
| `ò` | `ɔ` |
| `ny` | `ɲ` |
| `ng` | `ŋ` |
| `ñ` | `ɲ` |

## Evaluation Metrics

- **WER**: Word Error Rate
- **CER**: Character Error Rate  
- **MER**: Match Error Rate
- **WIL**: Word Information Lost
- **DER**: Diacritic Error Rate (tone mark accuracy)

## Running Tests
```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## References

- [Bambara Reference Corpus](http://cormand.huma-num.fr/)
- [Daba Morphological Analyzer](https://github.com/maslinych/daba)
- UNESCO Bamako Meeting (1966)
- Niamey African Reference Alphabet (1978)

## License

MIT License - see [LICENSE](LICENSE) for details.