"""Main module."""

import csv
from typing import List

import attr


@attr.s(auto_attribs=True)
class SongList:
    """List of songs."""

    songs: List[str]

    @classmethod
    def from_csv(cls: "SongList", csv_file_path: str) -> "SongList":
        """Generate a `SongList` instance from csv file.

        Args:
            csv_file_path: the file path stored songs data.

        Returns:
            A `SongList` instance.

        Raises:
            ValueError: if the csv header is incorrect.

        # noqa: DAR101 cls
        """
        songs = []
        with open(csv_file_path) as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    if "name" not in row.keys():
                        raise ValueError(f"Invalid csv header: {row.keys()}")
                else:
                    songs.append(row["name"])
                line_count += 1
        return cls(songs=songs)


if __name__ == "__main__":
    song_list = SongList.from_csv("docs/_data/songs.csv")
    print(song_list)
