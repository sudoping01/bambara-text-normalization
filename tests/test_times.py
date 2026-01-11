from datetime import time

import pytest

from bambara_normalizer import (
    bambara_to_duration,
    bambara_to_time,
    duration_to_bambara,
    format_duration_bambara,
    format_time_bambara,
    is_time_word,
    normalize,
    normalize_times_in_text,
    time_to_bambara,
)


class TestClockTimeToBambara:
    def test_whole_hour(self):
        result = time_to_bambara(1, 0)
        assert result == "Nɛgɛ kaɲɛ kelen"

    def test_with_minutes(self):
        result = time_to_bambara(1, 5)
        assert "Nɛgɛ kaɲɛ kelen" in result
        assert "tɛmɛnna" in result
        assert "sanga" in result
        assert "duuru" in result

    def test_7_30(self):
        result = time_to_bambara(7, 30)
        assert "Nɛgɛ kaɲɛ wolonwula" in result
        assert "tɛmɛnna" in result
        assert "bi saba" in result

    def test_13_50(self):
        result = time_to_bambara(13, 50)
        assert "Nɛgɛ kaɲɛ tan ni saba" in result
        assert "tɛmɛnna" in result
        assert "bi duuru" in result

    def test_midnight(self):
        result = time_to_bambara(0, 0)
        assert "fu" in result

    def test_noon(self):
        result = time_to_bambara(12, 0)
        assert "tan ni fila" in result


class TestBambaraToClockTime:
    def test_whole_hour(self):
        result = bambara_to_time("Nɛgɛ kaɲɛ kelen")
        assert result.hour == 1
        assert result.minute == 0

    def test_with_minutes(self):
        bambara = "Nɛgɛ kaɲɛ wolonwula tɛmɛnna ni sanga bi saba ye"
        result = bambara_to_time(bambara)
        assert result.hour == 7
        assert result.minute == 30


class TestFormatTimeBambara:
    def test_from_string(self):
        result = format_time_bambara("7:30")
        assert "wolonwula" in result
        assert "bi saba" in result

    def test_from_time_object(self):
        t = time(7, 30)
        result = format_time_bambara(t)
        assert "wolonwula" in result


class TestDurationToBambara:
    def test_minutes_only(self):
        result = duration_to_bambara(minutes=30)
        assert result == "miniti bi saba"

    def test_hours_and_minutes(self):
        result = duration_to_bambara(hours=1, minutes=30)
        assert "lɛrɛ kelen" in result
        assert "miniti bi saba" in result
        assert " ni " in result

    def test_full(self):
        result = duration_to_bambara(hours=1, minutes=30, seconds=10)
        assert "lɛrɛ kelen" in result
        assert "miniti bi saba" in result
        assert "segɔni tan" in result


class TestBambaraToDuration:
    def test_minutes_only(self):
        result = bambara_to_duration("miniti bi saba")
        assert result == (0, 30, 0)

    def test_hours_and_minutes(self):
        result = bambara_to_duration("lɛrɛ kelen ni miniti bi saba")
        assert result == (1, 30, 0)

    def test_full(self):
        result = bambara_to_duration("lɛrɛ kelen ni miniti bi saba ni segɔni tan")
        assert result == (1, 30, 10)


class TestFormatDurationBambara:
    def test_30min(self):
        result = format_duration_bambara("30min")
        assert result == "miniti bi saba"

    def test_1h30min(self):
        result = format_duration_bambara("1h30min")
        assert "lɛrɛ kelen" in result
        assert "miniti bi saba" in result

    def test_1h30min10s(self):
        result = format_duration_bambara("1h30min10s")
        assert "lɛrɛ kelen" in result
        assert "miniti bi saba" in result
        assert "segɔni tan" in result


class TestTimeTextNormalization:
    def test_clock_time(self):
        text = "A nana 7:30 la"
        result = normalize_times_in_text(text)
        assert "Nɛgɛ kaɲɛ wolonwula" in result
        assert "7:30" not in result

    def test_duration(self):
        text = "A tagara 1h30min"
        result = normalize_times_in_text(text)
        assert "lɛrɛ kelen" in result
        assert "miniti bi saba" in result

    def test_multiple(self):
        text = "A nana 7:30 la ani a tagara 30min kɔfɛ"
        result = normalize_times_in_text(text)
        assert "Nɛgɛ kaɲɛ" in result
        assert "miniti bi saba" in result


class TestIsTimeWord:
    def test_time_words(self):
        assert is_time_word("lɛrɛ") is True
        assert is_time_word("miniti") is True
        assert is_time_word("segɔni") is True

    def test_non_time_word(self):
        assert is_time_word("taa") is False


class TestTimeNormalizerIntegration:
    def test_with_expand_times(self):
        result = normalize("A nana 7:30 la", expand_times=True)
        assert "nɛgɛ kaɲɛ" in result
        assert "7:30" not in result

    def test_without_expand_times(self):
        result = normalize("A nana 7:30 la", expand_times=False, remove_punctuation=False)
        assert "7:30" in result

    def test_wer_preset_expands_times(self, wer_normalizer):
        result = wer_normalizer("A nana 7:30 la")
        assert "nɛgɛ kaɲɛ" in result


class TestTimeRoundTrip:
    def test_clock_time(self):
        original = time(7, 30)
        bambara = format_time_bambara(original)
        back = bambara_to_time(bambara)
        assert back.hour == original.hour
        assert back.minute == original.minute

    def test_duration(self):
        original = (1, 30, 10)
        bambara = duration_to_bambara(*original)
        back = bambara_to_duration(bambara)
        assert back == original


class TestTimeValidation:
    def test_invalid_hour_raises(self):
        with pytest.raises(ValueError):
            time_to_bambara(25, 0)

    def test_invalid_minute_raises(self):
        with pytest.raises(ValueError):
            time_to_bambara(1, 60)
