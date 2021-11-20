"""Tests for `legoworship` module."""
from typing import Generator

import pytest

from legoworship import Song, SongList, __version__


@pytest.fixture
def version() -> Generator[str, None, None]:
    """Sample pytest fixture."""
    yield __version__


def test_version(version: str) -> None:
    """Sample pytest test function with the pytest fixture as an argument."""
    assert version == "2021.11.0"


def test_song_pinyin_title() -> None:
    """The song title in pinyin."""
    assert Song(title="测试拼音").pinyin_title == ["Ce", "Shi", "Pin", "Yin"]


def test_song_pinyin_title_english() -> None:
    """English titles are splitted by words."""
    assert Song(title="Test Song").pinyin_title == ["Test", "Song"]


def test_song_pinyin_title_mixed() -> None:
    """Each language are handled independently."""
    assert Song(title="测试 Song").pinyin_title == ["Ce", "Shi", "Song"]


def test_song_pinyin_title_mixed_no_space() -> None:
    """Spaces are enforced when there is none."""
    assert Song(title="测试Song").pinyin_title == ["Ce", "Shi", "Song"]


def test_songlist_sort_by_pinyin_title_func() -> None:
    """The sort by pinyin function returns title in pinyin."""
    song = Song(title="测试")
    assert SongList._sort_by_pinyin_title(song) == ["Ce", "Shi"]


def test_songlist_sort_by_pinyin_title_asc() -> None:
    """Sorts a song list ascendingly by pinyin."""
    song_1 = Song(title="第一首")
    song_2 = Song(title="第二首")
    assert SongList(name="Test", songs=[song_1, song_2]).sort(by="title").songs == [song_2, song_1]


def test_songlist_sort_by_key() -> None:
    """Sorts a song list by key."""
    song_1 = Song(title="A", original_key="A")
    song_2 = Song(title="B", original_key="B")
    assert [song_1, song_2] == SongList(name="Test", songs=[song_1, song_2]).sort(
        by="original_key"
    ).songs
