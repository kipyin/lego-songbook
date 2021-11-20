"""Main module."""

import csv
import os
from pathlib import Path
from string import Template
from typing import Any, ClassVar, Dict, List, Mapping, Optional, Sequence, Type, TypeVar, Union

import attr
import yaml
from pypinyin import lazy_pinyin

# The default pinyin order for "祢" is "mí" first and then "nǐ", which is not
# how we pronounce the character.
PINYIN_ADJUSTMENTS = {ord("祢"): "nǐ,mí"}


SONG_PAGE_TEMPLATE = Template(
    """---
layout: song
title: $title
alternative_titles: $alternative_titles
lyricist: $lyricist
composer: $composer
---

"""
)


@attr.s(auto_attribs=True)
class SongResource:
    """A music sheet or a media file for a song.

    Args:
        song: A `Song` instance linked to this resource.
        resource_type: either "sheet" or "media".
        location: the path pointing to the resource file.
        bpm: the beats per minutes (tempo) of the resource.
        key: the musical key of the resource.
        artist: the artist of the resource.
        album: the album of the resource.
    """

    EXTENSIONS: ClassVar[Dict[str, List[str]]] = {
        "sheet": [".png", ".pdf"],
        "media": [".mp3", ".m4a", ".wav"],
    }

    # song: "Song"
    resource_type: str  # "sheet" or "media"
    location: str
    bpm: Optional[int] = None
    key: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None


SongType = TypeVar("SongType", bound="Song")


@attr.s(auto_attribs=True)
class Song:
    """A song."""

    title: str
    alternative_titles: Optional[List[str]] = None
    original_key: Optional[str] = None
    lyricist: Optional[str] = None
    composer: Optional[str] = None
    resources: Optional[List[SongResource]] = None
    lyrics: Optional[Mapping[str, str]] = None

    @property
    def pinyin_title(self: SongType) -> List[str]:
        """Return the title in pinyin.

        Each letter is capitalized, to sort with English titles.

        Examples:
            >>> Song("歌曲").pinyin_title
            ['Ge', 'Qu']
            >>> Song("歌曲 a song").pinyin_title
            ['Ge', 'Qu', 'A', 'Song']

        Returns:
            A list of each character's pinyin
        """
        return [pinyin.title() for pinyin in lazy_pinyin(self.title.split(" "))]

    @property
    def alternative_title_string(self: SongType) -> str:
        """Combine all alternative titles into one string."""
        return " / ".join(self.alternative_titles or [])

    def match_file(self: SongType, filename: str, extensions: List[str]) -> bool:
        """Match if a filename contains the searched title or one of the extensions."""
        if self.title in filename:
            for extension in extensions:
                if filename.endswith(extension):
                    return True
        return False

    def find_resources(
        self: SongType, resource_type: str, library: str, extension: Optional[str] = None
    ) -> bool:
        """Find and build song resources.

        Walk through each file in `library` and compare each song title with the filename,
        if there is a match, append it to a result list.

        Args:
            resource_type: "sheet" or "media".
            library: the path to search in.
            extension: match the extension if provided, otherwise a list of default
                extensions will be matched based on `resource_type`.

        Returns:
            True if resources are found, otherwise False

        Raises:
            ValueError: if `resource_type` does not match any of the default
                resource types.
        """
        if not extension and resource_type not in SongResource.EXTENSIONS:
            raise ValueError(f"Resource type of '{resource_type}' is not supported.")
        self.resources = [] if self.resources is None else self.resources
        search_extensions = [extension if extension else SongResource.EXTENSIONS[resource_type]]
        for root, _, files in os.walk(library):
            for file in files:
                if self.match_file(filename=file, extensions=search_extensions):
                    self.resources.append(
                        SongResource(
                            # song=self,
                            resource_type=resource_type,
                            location=os.path.join(root, file),
                        )
                    )
        return True if self.resources else False

    def load_info_from_list(
        self: SongType, song_info_list: Sequence[Mapping[str, Any]]
    ) -> Optional[bool]:
        """Load a song_info.yaml into self.resources and self.lyrics."""
        for song_info in song_info_list:
            if self.title == song_info["title"]:
                if "lyrics" in song_info and song_info["lyrics"]:
                    self.lyrics = song_info["lyrics"]
                if "resources" in song_info and song_info["resources"]:
                    song_info_resources = song_info["resources"]
                    self.resources = self.resources or []
                    for resource in song_info_resources:
                        self.resources.append(
                            SongResource(
                                resource_type=resource["type"],
                                location=resource["location"],
                                artist=resource["artist"],
                                album=resource["album"],
                                key=resource["key"],
                                bpm=resource["bpm"],
                            )
                        )
                break
        return self.resources

    @property
    def info(self: SongType) -> Dict:
        """Song info."""
        song_info = dict()
        song_info["title"] = self.title
        if self.resources:
            song_info["resources"] = [attr.asdict(r) for r in self.resources]
        else:
            song_info["resources"] = None
        song_info["lyrics"] = self.lyrics or None
        return song_info

    def check_page_exists(self: SongType, page_dir: str) -> bool:
        """Check if the song's page exists in `page_dir`."""
        # TODO: first should check if `page_dir` exists.
        if not os.path.isdir(page_dir):
            raise ValueError(f"{page_dir} is not a valid page directory.")
        return os.path.isfile(os.path.join(page_dir, self.title, ".md"))

    def create_page(self: SongType, page_dir: str, quiet: bool = False) -> bool:
        """Create a song's page if it does not exist."""
        if self.check_page_exists(page_dir):
            if quiet:
                return False
            else:
                raise ValueError(f"Song page for {self.title} already exists.")
        os.mkdir(os.path.join(page_dir, self.title, ".md"))
        return True


SongListType = TypeVar("SongListType", bound="SongList")


@attr.s(auto_attribs=True)
class SongList:
    """A collection of `Song` instances.

    Args:
        name: the name of the song list, could be anything.
        songs: the list containing all songs.
    """

    _LEGACY_HEADER: ClassVar[List[str]] = ["name", "key", "hymn_ref", "sheet_type"]
    _HEADER: ClassVar[List[str]] = [
        "title",
        "original_key",
        "alternative_titles",
        "lyricist",
        "composer",
    ]
    name: str
    songs: List[Song]

    @staticmethod
    def _sort_by_pinyin_title(song: Song) -> Sequence[str]:
        """Sort function (by the pinyin title) used in self.sort()."""
        return song.pinyin_title

    @staticmethod
    def _sort_by_original_key(song: Song) -> Optional[str]:
        """Sort function (by the song's key) used in self.sort()."""
        return song.original_key

    def sort(self: SongListType, by: str, desc: bool = False, legacy: bool = False) -> "SongList":
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
            elif by in ["key", "original_key"]:
                sort_func = self._sort_by_original_key
            else:
                raise NotImplementedError(f"Sorting by {by} is not supported.")
        else:
            raise ValueError(f"{by} is not a valid sort key.")

        sorted_songs = sorted(self.songs, key=sort_func, reverse=desc)
        return SongList(name=self.name, songs=sorted_songs)

    def export_csv(self: SongListType, to: str, legacy: bool = False) -> bool:
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
                            "alternative_titles": song.alternative_title_string,
                            "original_key": song.original_key,
                            "lyricist": song.lyricist,
                            "composer": song.composer,
                        }
                    )
            return True

    def export_song_info(self: SongListType, to: str) -> bool:
        """Export song resources and lyrics to docs/_data/song_info.yaml."""
        song_info_list = []
        for song in self.songs:
            song_info_list.append(song.info)
        with open(to, "w") as stream:
            yaml.dump(
                song_info_list,
                stream=stream,
                allow_unicode=True,
                sort_keys=False,
                default_flow_style=False,
            )
        return True

    def info(self: SongListType) -> List:
        """Song info list."""
        # song_info_list = []
        # for song in self.songs:
        #     song_info_list

    def load_info_from_yaml(self: SongListType, from_: str) -> bool:
        """Load song info from song_info.yaml."""
        with open(from_, "r") as stream:
            song_info_list = yaml.safe_load(stream)
        for song in self.songs:
            song.load_info_from_list(song_info_list)
        return True

    def _add_song(self: SongListType, song: Song) -> bool:
        """Add a song to the list."""
        if isinstance(song, Song):
            self.songs.append(song)
            return True
        else:
            raise ValueError(f"Cannot add {song} ({type(song)}) to the song list.")

    def _add_song_list(self: SongListType, songlist: "SongList") -> bool:
        """Add another song list to this song list."""
        if isinstance(songlist, SongList):
            self.songs = self.songs + songlist.songs
            return True
        else:
            raise ValueError(f"Cannot add {songlist} ({type(songlist)}) to the song list.")

    def add(self: SongListType, songs: Union[Song, "SongList"]) -> bool:
        """Add another song or songlist to the song list."""
        if isinstance(songs, Song):
            self._add_song(songs)
            return True
        elif isinstance(songs, SongList):
            self._add_song_list(songs)
            return True
        else:
            raise ValueError(f"Cannot add {songs} ({type(songs)}) to the song list.")

    @classmethod
    def from_csv(
        cls: Type[SongListType], csv_file_path: str, legacy: bool = False
    ) -> SongListType:
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


def find(title: str, what: str, path: str) -> Union[List[str], bool]:
    """Find a song in path."""
    if what not in ["sheet", "media"]:
        raise ValueError(f"Only `sheet` and `media` are supported, not {what}.")
    results = []
    for dirpath, _, files in os.walk(path):
        for filename in files:
            if what == "sheet":
                if title in filename and filename.endswith(".png") and "TINY" in dirpath:
                    found_path = os.path.join(dirpath, filename)
                    print(found_path)
                    results.append(found_path)
            elif what == "media":
                if title in filename and filename.endswith(".mp3"):
                    found_path = os.path.join(dirpath, filename)
                    print(found_path)
                    results.append(found_path)
            else:
                pass
    if not results:
        print(f"no results found for {title} in {path}")
        return False
    return results


def find_multiple(what: str, path: str, song_list: SongList) -> Union[List[str], bool]:
    """Find multiple _songs in a song list."""
    results = []
    for dirpath, _, files in os.walk(path):
        for filename in files:
            for song in song_list.songs:
                if song.title in filename:
                    if (what == "sheet" and filename.endswith(".png") and "TINY" in dirpath) or (
                        what == "media" and filename.endswith(".mp3")
                    ):
                        found_path = os.path.join(dirpath, filename)
                        print(song.title)
                        print(found_path)
                        results.append(found_path)
    return results


if __name__ == "__main__":
    # import subprocess  # noqa
    from pprint import pprint

    #
    # SHEET_LIB = "/Users/kip/Mercury/3.Ecclasia/4. 灵栖清泉"
    # MUSIC_LIB = "/Volumes/music"
    # song_list = SongList.from_csv(csv_file_path="docs/_data/all_songs.csv", legacy=False)
    # song = song_list.songs[-2]
    # pprint(f"Song: {song.title}")
    # song.find_resources("sheet", library=SHEET_LIB, extension=".pdf")
    # pprint([x.location for x in song.resources])
    # subprocess.Popen('open "{song.resources[0].location}"', shell=True)  # noqa
    song_list = SongList.from_csv(csv_file_path="docs/_data/songs.csv", legacy=False)
    # song_list.sort(by="title").export_csv(to="docs/_data/songs.csv")
    song = song_list.songs[1]
    song_list.load_info_from_yaml(from_="docs/_data/song_info.yaml")
    pprint(song_list.export_song_info(to="docs/_data/song_info_test.yaml"))
