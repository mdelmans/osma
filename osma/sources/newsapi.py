"""
"""
import favicon
from datetime import datetime

from newsapi import NewsApiClient
from newsapi.newsapi_exception import NewsAPIException
from ..api import SourceBase, CoverageEntry, Query, ANDQuery


class NewsAPISource(SourceBase):
    PAGE_SIZE = 100

    def __init__(self, api_key):
        self._client = NewsApiClient(api_key=api_key)

    def convert_query(self, query: Query) -> str:
        if isinstance(query, ANDQuery):
            return " AND ".join(query.keywords)
        else:
            raise TypeError("Only supporting AND queries at the moment")

    def get_query_results(self, query: str, from_timestamp: datetime = None):
        try:
            response = self._client.get_everything(
                q=query,
                from_param=from_timestamp,
                sort_by='publishedAt',
                page_size=self.PAGE_SIZE
            )
        except NewsAPIException as e:
            response = self._client.get_everything(
                q=query,
                sort_by='publishedAt',
                page_size=self.PAGE_SIZE
            )
        return response['articles']

    def result_to_entry(self, result) -> CoverageEntry:
        logo = None
        icons = favicon.get(result['url'])
        if len(icons) > 0:
            logo = icons[0]
        entry = self._create_new_entry(
            actor_primary=result['source']['name'],
            actor_secondary=result['author'],
            actor_logo=logo.url,
            date=datetime.strptime(
                result['publishedAt'],
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            body=result['description'],
            title=result['title'],
            url=result['url'],
            image_url=result['urlToImage']
        )
        return entry
