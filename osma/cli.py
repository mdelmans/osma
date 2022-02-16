"""OSMA CLI
"""

import sys
import click
import toml
from loguru import logger

from osma.api import SourceMeta, AggregatorMeta, QueryMeta

logger.add(
    sys.stderr,
    format="{time} {level} {message}",
    level="INFO"
)


@click.group()
@click.option('--config', '-c', type=click.File('r'))
@click.pass_context
def osma(ctx, config):
    conf_dict = toml.load(config)
    ctx.ensure_object(dict)

    ctx.obj['sources'] = []
    if 'sources' in conf_dict:
        for _, source_dict in conf_dict['sources'].items():
            source_type_name = source_dict.get('type', None)
            if source_type_name in SourceMeta.__sources__:
                del source_dict['type']
                source = SourceMeta.__sources__[source_type_name](
                    **source_dict
                )
                ctx.obj['sources'].append(source)

    ctx.obj['aggregators'] = []

    if 'aggregators' in conf_dict:
        for _, agg_dict in conf_dict['aggregators'].items():
            agg_type_name = agg_dict.get('type', None)
            if agg_type_name in AggregatorMeta.__aggs__:
                del agg_dict['type']

                query = None
                if 'query' in agg_dict:
                    query_dict = agg_dict.get('query', {})
                    query_type_name = query_dict.get('type', None)
                    if query_type_name in QueryMeta.__queries__:
                        del query_dict['type']
                        query = QueryMeta.__queries__[query_type_name](
                           ** query_dict
                        )
                del agg_dict['query']
                agg = AggregatorMeta.__aggs__[agg_type_name](
                    sources=ctx.obj['sources'],
                    query=query,
                    **agg_dict
                )
                ctx.obj['aggregators'].append(agg)


@osma.command()
@click.pass_context
def run(ctx):
    for aggregator in ctx.obj['aggregators']:
        logger.info(f'Starting {aggregator.__class__.__name__}')
        aggregator.run()


if __name__ == '__main__':
    osma()
