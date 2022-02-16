"""Jekyll aggregator.

Fetches entries from sources and converts them into frontmatter Posts.
"""
from typing import Dict, Any

import hashlib
from datetime import datetime
import frontmatter
from frontmatter import Post
from dataclasses import dataclass, asdict
import json
import os

from ..api import CoverageAggreagatorBase, Entry


@dataclass
class JekyllCoverageAggregator(CoverageAggreagatorBase):
    """Jekyll coverage aggregator.

    Attributes:
        post_location: Output path for frontmatter posts.
        last_post_dates_file_name: Path to file storing dates of last posts
            for each source.
    """
    post_location: str
    last_post_dates_file_name: str 

    def get_last_entry_date(self, source_name: str) -> datetime:
        """Gets date of the last entry for the source.

        Args:
            source_name: Name of the source to fetch the date for.

        Returns:
            A datetime object representing the date of the last entry
            in UTC.
        """
        if not os.path.exists(self.last_post_dates_file_name):
            with open(self.last_post_dates_file_name, 'w') as f:
                json.dump(
                    {s.__class__.__name__: None for s in self.sources},
                    f
                )

        with open(self.last_post_dates_file_name, 'r') as f:
            sources = json.load(f)
            timestamp = sources.get(source_name, None)
            if timestamp is not None:
                return datetime.fromtimestamp(int(timestamp)+1)
            else:
                return None

    def set_last_entry_date(
            self, source_name: str, timestamp: datetime) -> None:
        """Sets date of the last entry for the source.

        Args:
            source_name: Name of the source to set the date for.
            timestamp: Timestamp to set.
        """
        with open(self.last_post_dates_file_name, 'r') as f:
            sources = json.load(f)

        sources[source_name] = timestamp.timestamp()

        with open(self.last_post_dates_file_name, 'w') as f:
            f.write(json.dumps(sources))

    @staticmethod
    def entry_to_tags(entry: Entry) -> Dict[str, Any]:
        """Converts entry to dictionary of post tags.

        Args:
            entry: Input entry.

        Returns:
            A dictionary of tags.
        """
        tags = asdict(entry)
        del(tags['body'])
        tags['date'] = tags['date'].timestamp()
        return tags

    @staticmethod
    def encode_tags(tags: Dict[str, Any]) -> str:
        """Encodes tags to md5 hash.

        Helps to assign a unique id for each post.

        Args:
            tags: A dictionary of tags.

        Returns:
            md5 hexidigest string.
        """
        m = hashlib.md5()
        keys = ['actor_primary', 'actor_secondary', 'date', '_source_cls']
        for key in keys:
            m.update(str(tags.get(key)).encode())
        return m.hexdigest()

    def save_entry(self, entry: Entry) -> None:
        """Saves entry to the post location.
        
        Converts entry to a post, and saves it to the post location.

        Args:
            entry: Input entry.
        """
        tags = self.entry_to_tags(entry)
        entry_timestamp = tags['date']

        created_at = datetime.fromtimestamp(entry_timestamp).strftime(
            "%Y-%m-%d"
        )
        title = self.encode_tags(tags)
        new_entry_file_name = f"{created_at}-{title}.txt"

        new_entry_path = os.path.join(self.post_location, new_entry_file_name)

        if not os.path.exists(new_entry_path):
            with open(new_entry_path, 'wb') as f:
                post = Post(
                    content=entry.body,
                    osma=tags
                )
                frontmatter.dump(post, fd=f)
