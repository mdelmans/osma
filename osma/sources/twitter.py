from tweepy import Client
from ..api import SourceBase, Query, ANDQuery, CoverageEntry


class TwitterSource(SourceBase):
    def __init__(self,  access_token, access_token_secret,
                 consumer_key, consumer_secret, bearer_token):
        self._client = Client(
            access_token=access_token,
            access_token_secret=access_token_secret,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            bearer_token=bearer_token
        )

    def convert_query(self, query: Query) -> str:
        if isinstance(query, ANDQuery):
            return "-is:retweet " + " ".join(query.keywords)
        else:
            raise TypeError("Only supporting AND queries at the moment") 

    def get_query_results(self, query: str, from_timestamp: int = None):
        posts = []
        kwargs = {
            "query": query,
            "expansions": ['author_id', 'attachments.media_keys'],
            "user_fields": ['name', 'username', 'profile_image_url'],
            "tweet_fields": ['created_at', 'context_annotations'],
            "media_fields": ['preview_image_url', 'height', 'url']
        }
        new_posts, incs, x, info = self._client.search_recent_tweets(
            start_time=from_timestamp,
            **kwargs
        )

        while new_posts:
            if 'media' not in incs:
                incs['media'] = [None for _ in range(len(new_posts))]
            posts.extend([
                (post, inc, media)
                for post, inc, media
                in zip(new_posts, incs['users'], incs['media'])
                ]
            )
            new_posts, incs, _, info = self._client.search_recent_tweets(
                since_id=info['newest_id'],
                **kwargs
            )
        return posts
    
    def result_to_entry(self, result) -> CoverageEntry:
        entry = self._create_new_entry(
            actor_primary=result[1].name,
            actor_secondary=result[1].username,
            actor_logo=result[1].profile_image_url,
            date=result[0].created_at,
            body=result[0].text,
            title=result[0].text,
            image_url=getattr(result[2], 'url', None)
        )
        return entry
