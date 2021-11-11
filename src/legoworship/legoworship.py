"""Main module."""

import csv
from pathlib import Path
from typing import ClassVar, List, TypeVar

import attr
from pypinyin import lazy_pinyin

# The default pinyin order for "祢" is "mí" first and then "nǐ", which is not
# how we pronounce the character.
PINYIN_ADJUSTMENTS = {ord("祢"): "nǐ,mí"}


T = TypeVar("T")


@attr.s(auto_attribs=True)
class Song:
    """A song."""

    title: str
    original_key: str = None
    bpm: int = None
    lyricist: str = None
    composer: str = None

    @property
    def pinyin_title(self: T) -> List[str]:
        """Return the title in pinyin.

        Each letter is capitalized, to sort with English titles.

        Examples:
            >>> Song("歌曲").pinyin_title
            ["Ge", "Qu"]
            >>> Song("歌曲 a song").pinyin_title
            ["Ge", "Qu", "A", "Song"]

        Returns:
            A list of each character's pinyin
        """
        return [pinyin.title() for pinyin in lazy_pinyin(self.title.split(" "))]


@attr.s(auto_attribs=True)
class SongList:
    """A collection of `Song` instances.

    Args:
        name: the name of the song list, could be anything.
        songs: the list containing all songs.
    """

    _LEGACY_HEADER: ClassVar[List[str]] = ["name", "key", "hymn_ref", "sheet_type"]
    _HEADER: ClassVar[List[str]] = ["title", "original_key", "bpm", "lyricist", "composer"]
    name: str
    songs: List[Song]

    @staticmethod
    def _sort_by_pinyin_title(song: Song) -> List[str]:
        """Sort function (by the pinyin title) used in self.sort()."""
        return song.pinyin_title

    def sort(self: T, by: str, desc: bool = False, legacy: bool = False) -> T:
        """Order the list by any of the header item.

        Args:
            by: the sort key.
            desc: sort in descending order if True, else in ascending order.
            legacy: whether or not the format is legacy.

        Raises:
            NotImplementedError: if the sort key is a valid header but not yet implemented.
            ValueError: if the sort key is not a valid header item.

        Returns:
            A sorted `SongList` instance.
        """
        if (legacy and by in self._LEGACY_HEADER) or (not legacy and by in self._HEADER):
            if by == "title":
                sort_func = self._sort_by_pinyin_title
            else:
                raise NotImplementedError(f"Sorting by {by} is not supported.")
        else:
            raise ValueError(f"{by} is not a valid sort key.")

        sorted_songs = sorted(self.songs, key=sort_func, reverse=desc)
        return SongList(name=self.name, songs=sorted_songs)

    def export_csv(self: T, to: str, legacy: bool = False) -> bool:
        """Export the songlist to a csv file."""
        filenames = self._LEGACY_HEADER if legacy else self._HEADER
        with open(to, "w") as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=filenames)
            csv_writer.writeheader()
            if legacy:
                for song in self.songs:
                    csv_writer.writerow(
                        {
                            "name": song.title,
                            "key": song.original_key,
                            "hymn_ref": None,
                            "sheet_type": None,
                        }
                    )
            else:
                for song in self.songs:
                    csv_writer.writerow(
                        {
                            "title": song.title,
                            "original_key": song.original_key,
                            "bpm": song.bpm,
                            "lyricist": song.lyricist,
                            "composer": song.composer,
                        }
                    )
            return True

    @classmethod
    def from_csv(cls: T, csv_file_path: str, legacy: bool = False) -> T:
        """Generate a `SongList` instance from csv file.

        Args:
            csv_file_path: the file path stored songs data.
            legacy: whether or not the csv file to read is in legacy format.

        Returns:
            A `SongList` instance.

        Raises:
            ValueError: raise if the csv header is incorrect.

        # noqa: DAR101 cls
        """
        songs = []
        header = cls._LEGACY_HEADER if legacy else cls._HEADER
        with open(csv_file_path) as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    if list(row.keys()) != header:
                        raise ValueError(f"Invalid csv header: {row.keys()}")
                else:
                    if legacy:
                        songs.append(Song(title=row["name"], original_key=row["key"]))
                    else:
                        songs.append(Song(title=row["title"], original_key=row["original_key"]))
                line_count += 1
        return cls(name=Path(csv_file_path).name, songs=songs)


if __name__ == "__main__":
    song_list = SongList.from_csv("docs/_data/songs.csv", legacy=True)
    print(song_list)
    song_list.songs.append(Song(title="爱赢了", original_key="C"))
    song_list.sort(by="title", legacy=False).export_csv(to="docs/_data/all_songs.csv")
