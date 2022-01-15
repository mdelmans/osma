from typing import List, TypeVar, Optional
from datetime import datetime
from dataclasses import dataclass
from abc import ABCMeta, abstractmethod


@dataclass
class CoverageEntry:
    """Coverage entry.
    
    A standard data class for representing a coverage entry.
    
    Args:
        actor_primary: A primary name of the author.
        actor_secondary: A secondary name of the author.
        score: Number representing engagement with the entry, for e.g.
            number of likes or upvotes.
        country: Country of entry origin.
        actor_logo: URL to the actor's logo.
        date: Date of the entry creation.
        body: Body of the entry.
        url: URL to the full entry.
        title: Title of the entry.
        image_url: URL to the media image.

    Attrs:
        actor_primary: A primary name of the author.
        actor_secondary: A secondary name of the author.
        score: Number representing engagement with the entry, for e.g.
            number of likes or upvotes.
        country: Country of entry origin.
        actor_logo: URL to the actor's logo.
        date: Date of the entry creation.
        body: Body of the entry.
        url: URL to the full entry.
        title: Title of the entry.
        image_url: URL to the media image.
    """
    _source_cls: str
    actor_primary: str
    actor_secondary: str
    date: datetime
    body: str
    score: Optional[int] = None
    country: Optional[str] = None
    actor_logo: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    image_url: Optional[str] = None


class QueryMeta(type):
    __queries__ = {}

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if name not in QueryMeta.__queries__:
            QueryMeta.__queries__[name] = cls


class Query(metaclass=QueryMeta):
    """A base class for defying queries"""
    pass


@dataclass
class ANDQuery(Query):
    """AND query.

    A query that is formed by matching all given keywords.

    Attrs:
        keywords: A list of keywords.
    """
    keywords: List[str]


@dataclass
class ORQuery(Query):
    """OR query.

    A query that is formed by matching at least one of the given
    keywords.

    Attrs:
        keywords: A list of keywords.
    """
    keywords: List[str]


R = TypeVar('R')


class SourceMeta(ABCMeta):
    __sources__ = {}

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if name not in SourceMeta.__sources__:
            SourceMeta.__sources__[name] = cls


class SourceBase(metaclass=SourceMeta):
    """A source base class.

    Source classes are responsible for fetching new entries for the given
    query and converting them to coverage entries.
    """
    @abstractmethod
    def convert_query(self, query: Query) -> str:
        """Converts query from a standard definition to a string
        specific to the source.

        Args:
            query: A query object.

        Returns:
            A string representation of the source-specific query.

        Raises:
            TypeError: If query type is not supported.
        """
        pass

    @abstractmethod
    def get_query_results(
            self,
            query: str,
            from_timestamp: Optional[datetime] = None
            ) -> List[R]:
        """Gets intermediate query result.

        Args:
            query: A string representing source-specific query.
            from_timestamp: Minimal datetime of the entry to querry.

        Returns:
            A list of objects, each rrepresenting an enrty in a
            source-specific format. If ``from_timestamp`` is given,
            must only return entries that are past the timestamp.
        """
        pass

    @abstractmethod
    def result_to_entry(self, result: R) -> CoverageEntry:
        """Converts entry from a soure-specific format to a standard
        entry object.

        Args:
            result: A source-specific entry object.

        Returns:
            Converted coverage entry object. 
        """
        pass

    def fetch_entries(
            self,
            query: Query,
            from_timestamp: datetime = None
            ) -> List[CoverageEntry]:
        """Fetches entries from the source.

        Args:
            query: A query to use for fetching the entries.
            from_timestamp: A minimal date of entry.

        Returns:
            A list of the coverage entries that satisfy the given
            ``query`` and are past the given timestamp.
        """
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

        for res in results:
            try:
                yield self.result_to_entry(res)
            except BaseException as e:
                print(f"Could not convert result to entry: {e}")

    @classmethod
    def _create_new_entry(cls, **kwargs):
        return CoverageEntry(
            _source_cls=cls.__name__,
            **kwargs
        )


class AggregatorMeta(ABCMeta):
    __aggs__ = {}

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if name not in AggregatorMeta.__aggs__:
            AggregatorMeta.__aggs__[name] = cls


@dataclass
class CoverageAggreagatorBase(metaclass=AggregatorMeta):
    """A base class for coverage aggregator.
    
    Aggregators collect coverage entries from the given set of sources
    using the given standard query and save them.
    
    Args:
        sources: A list of sources.
        query: A query to use for fetching the entries.

    Attrs:
        sources: A list of sources.
        query: A query to use for fetching the entries.
    """
    sources: List[SourceBase]
    query: str

    @abstractmethod
    def save_entry(self, entry: CoverageEntry) -> None:
        """Saves entry.
        """
        pass

    @abstractmethod
    def get_last_entry_date(self, source_name: str) -> Optional[datetime]:
        """Gets the date of the last entry for the given source.

        The returned timestamp is used as a ``from_timestamp`` argument
        for filtering query results in the sources.

        Should be used in conjunction with ``set_last_entry_date`` to
        create a system for saving the dates of the last entries for
        every source.

        Args:
            source_name: Name of the source class to get the last entry
            date for.
        Returns:
            Date of the last fetched entry.
        """
        pass

    @abstractmethod
    def set_last_entry_date(self, source_name: str,
                            timestamp: datetime) -> None:
        """Sets the date of the last entry for the given source.

        Should be used in conjunction with ``set_last_entry_date`` to
        create a system for saving the dates of the last entries for
        every source.

        Args:
            source_name: Name of the source class to set the last entry
            date for.
            timestamp: Date to set.
        """
        pass

    def run(self) -> None:
        """Runs aggregator.

        For each source, fetches entries that are newer than the last
        entry date as defined in ``get_last_entry_date`` and saves them
        using ``save_entry`` method. Then updates the last entry date
        using ``set_last_entry_date`` method.
        """
        for source in self.sources:
            source_name = source.__class__.__name__
            last_entry_date = self.get_last_entry_date(source_name)

            new_entries = source.fetch_entries(
                self.query,
                from_timestamp=last_entry_date
            )

            for entry in new_entries:
                self.save_entry(entry)
                if (
                        last_entry_date is None
                        or entry.date > last_entry_date
                ):
                    last_entry_date = entry.date
            
            if last_entry_date is not None:
                self.set_last_entry_date(source_name, last_entry_date)
