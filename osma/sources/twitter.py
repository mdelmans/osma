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

    def get_query_results(self, query:str, from_timestamp: int=None):
        posts=[]
        new_posts, incs, _,info = self._client.search_recent_tweets(
            query=query,
            start_time=from_timestamp,
            expansions=['author_id', 'attachments.media_keys'],
            user_fields=['name', 'username','profile_image_url'],
            tweet_fields=['created_at', 'context_annotations'],
            media_fields=['preview_image_url', 'height', 'url']
        )

        while new_posts:
            posts.extend( [(post, inc, media) for post, inc, media in zip(new_posts, incs['users'], incs['media'])] )
            new_posts, incs, _,info = self._client.search_recent_tweets(
                query=query,
                since_id=info['newest_id'],
                expansions=['author_id', 'attachments.media_keys'],
                user_fields=['name', 'username','profile_image_url'],
                tweet_fields=['created_at', 'context_annotations'],
                media_fields=['preview_image_url', 'height', 'url']
            )
        return posts
    
    def result_to_entry(self, result) -> CoverageEntry:
        entry = CoverageEntry(
            source_cls="TwitterSource",
            actor_primary=result[1].name,
            actor_secondary=result[1].username,
            reach=None,
            country=None,
            actor_logo=result[1].profile_image_url,
            date=result[0].created_at,
            body=result[0].text,
            title=result[0].text,
            url=None,
            image_url=result[2].url
        )
        return entry