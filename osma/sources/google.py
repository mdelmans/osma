import favicon
from datetime import datetime
from ..api import SourceBase, CoverageEntry, Query, ANDQuery

from newsapi import NewsApiClient

class GoogleNewsSource(SourceBase):
    PAGE_SIZE = 100

    def __init__(self, api_key):
        self._client = NewsApiClient(api_key=api_key)

    def convert_query(self, query: Query) -> str:
        if isinstance(query, ANDQuery):
            return " AND ".join(query.keywords)
        else:
            raise TypeError("Only supporting AND queries at the moment")

    def get_query_results(self, query:str, from_timestamp: datetime=None):
        response = self._client.get_everything(
            q=query,
            from_param=from_timestamp,
            sort_by='publishedAt',
            page_size=GoogleNewsSource.PAGE_SIZE
        )
        return response['articles']


    def result_to_entry(self, result) -> CoverageEntry:
        logo = None
        icons = favicon.get(result['url'])
        if len(icons) > 0:
            logo = icons[0]
        entry = CoverageEntry(
            source_cls="GoogleNewsSource",
            actor_primary=result['source']['name'],
            actor_secondary=result['author'],
            reach=None,
            country=None,
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