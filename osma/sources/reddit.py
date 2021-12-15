from datetime import datetime
from ..api import SourceBase, CoverageEntry, Query, ANDQuery

from praw import Reddit

class RedditSource(SourceBase):
    def __init__(self, client_id, secret, user_agent):
        self._client = Reddit(
            client_id=client_id,
            client_secret=secret,
            user_agent=user_agent
        )

    def convert_query(self, query: Query) -> str:
        if isinstance(query, ANDQuery):
            return " AND ".join(
                [
                    f"((self:yes selftext:{kwrd}) OR (title:{kwrd}))"
                    for kwrd in query.keywords
                ]
            )
        else:
            raise TypeError("Only supporting AND queries at the moment")

    def get_query_results(self, query:str, from_timestamp: datetime=None):
        listings = self._client.subreddit("all").search(query, sort='new')
        if from_timestamp is None:
            return listings
        else:
            res = []
            for post in listings:
                if post.created_utc > from_timestamp.timestamp():
                    res.append(post)
                else:
                    break
            return res

    def result_to_entry(self, result) -> CoverageEntry:
        entry = CoverageEntry(
            source_cls=RedditSource,
            actor_primary=result.author.name,
            actor_secondary=result.subreddit.display_name,
            reach=result.score,
            country=None,
            actor_logo=None,
            date=datetime.fromtimestamp(result.created_utc),
            body=result.title + '\n' + result.selftext,
            url=result.url
        )
        return entry