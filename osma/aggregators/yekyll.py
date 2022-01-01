import hashlib
from datetime import datetime
import frontmatter
from frontmatter import Post
from dataclasses import dataclass, asdict
import json
import os

from ..api import CoverageAggreagatorBase


@dataclass
class YekyllCoveageAggregator(CoverageAggreagatorBase):
	entry_location: str
	last_post_dates_file_name:str 

	def get_last_entry_date(self, source):
		if not os.path.exists(self.last_post_dates_file_name):
			with open(self.last_post_dates_file_name,'w') as f:
				json.dump({s.__class__.__name__: None for s in self.sources},f)

		with open(self.last_post_dates_file_name, 'r') as f:
			sources = json.load(f)
			timestamp = sources.get(source, None)
			if timestamp is not None:
				return datetime.fromtimestamp(int(timestamp)+1)
			else:
				return None

	def update_source_entry(self, source, timestamp):
		with open(self.last_post_dates_file_name, 'r') as f:
			sources = json.load(f)
			old_timestamp = sources.get(source, None)
			if old_timestamp is None or timestamp > old_timestamp:
				sources[source] = timestamp

		with open(self.last_post_dates_file_name, 'w') as f:
			f.write(json.dumps(sources))

	@staticmethod
	def entry_to_tags(entry):
		tags = asdict(entry)
		del(tags['body'])
		tags['date'] = tags['date'].timestamp()
		return tags

	@staticmethod
	def encode_tags(tags):
		m = hashlib.md5()
		keys = ['actor_primary', 'actor_secondary', 'date', 'source_cls']
		for key in keys:
			m.update(str(tags.get(key)).encode())
		return m.hexdigest()

	def save_entry(self, entry):
		tags = self.entry_to_tags(entry)
		entry_timestamp = tags['date']

		created_at = datetime.fromtimestamp(entry_timestamp).strftime(
			"%Y-%m-%d"
		)
		title = self.encode_tags(tags)
		new_entry_file_name = f"{created_at}-{title}.txt"

		with open(os.path.join(self.entry_location, new_entry_file_name), 'wb') as f:
			post = Post(
				content=entry.body,
				osma=tags
			)
			frontmatter.dump(post, fd=f)

		self.update_source_entry(tags['source_cls'], entry_timestamp)
