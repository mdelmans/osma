from typing import List, TypeVar, Optional
from datetime import datetime
from dataclasses import dataclass

@dataclass
class CoverageEntry:
    source_cls: str
    actor_primary: str
    actor_secondary: str
    reach: int
    country: str
    actor_logo: str
    date: datetime
    body: str
    url: str
    title: str
    image_url: str

class Query:
    pass

@dataclass
class ANDQuery(Query):
    keywords: List[str]

@dataclass
class ORQuery(Query):
    keywords: List[str]

R = TypeVar('R')
class SourceBase:
    def convert_query(self, query: Query) -> str:
        pass

    def get_query_results(self, query:str, from_timestamp: datetime=None) -> List[R]:
        pass

    def result_to_entry(self, result: R) -> CoverageEntry:
        pass

    def fetch_entries(self, query: Query, from_timestamp: datetime=None) -> List[CoverageEntry]:
        try:
            specific_query = self.convert_query(query)
        except BaseException as e:
            raise RuntimeError(
                "Could not convert input query to a specific one"
            ) from e
        try:
            results = self.get_query_results(specific_query, from_timestamp)
        except ConnectionError as e:
            raise ConnectionError("Failed to get query results") from e
        except BaseException as e:
            raise RuntimeError("Failed to get query results") from e

        try:
            entries = [self.result_to_entry(res) for res in results]
        except BaseException as e:
            raise RuntimeError("Failed to generate coverage entries") from e

        return entries

@dataclass
class CoverageAggreagatorBase:
    sources: List[SourceBase]
    query: str

    def save_entry(self, entry: CoverageEntry):
        pass

    def get_last_entry_date(self, source) -> Optional[datetime]:
        pass

    def run(self):
        for source in self.sources:
            last_entry_date = self.get_last_entry_date(source.__class__.__name__)
            new_entries = source.fetch_entries(
                self.query,
                from_timestamp=last_entry_date
            )
            for entry in new_entries:
                self.save_entry(entry)



