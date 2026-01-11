import pytest

from bambara_normalizer import BambaraNormalizer, BambaraNormalizerConfig


@pytest.fixture
def normalizer():
    return BambaraNormalizer()


@pytest.fixture
def wer_normalizer():
    config = BambaraNormalizerConfig.for_wer_evaluation()
    return BambaraNormalizer(config)


@pytest.fixture
def contract_normalizer():
    config = BambaraNormalizerConfig(contraction_mode="contract")
    return BambaraNormalizer(config)


@pytest.fixture
def preserve_normalizer():
    config = BambaraNormalizerConfig(contraction_mode="preserve")
    return BambaraNormalizer(config)


@pytest.fixture
def tone_preserving_normalizer():
    config = BambaraNormalizerConfig.preserving_tones()
    return BambaraNormalizer(config)
