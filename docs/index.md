# Welcome to OSMA

OSMA stands for Open Social Media Aggregator. It combines APIs of most common social media platforms and allows you to query multiple sources at once for new entries.

Currently, OSMA uses the following social media APIs:

* Twitter using [tweepy](https://www.tweepy.org/)
* Reddit using [praw](https://praw.readthedocs.io/en/stable/)
* NewsAPI using [newsapi](https://newsapi.org/docs/client-libraries/python)

You can easily extend OSMA to use other APIs, check out [Add a new source] on how to do it.

At the moment, OSMA only supports [Jekyll](https://jekyllrb.com/) as an aggregator frontend. But you can easily add your own. See [Add a new aggregator] on how to do it.


## Installation

OSMA is availabe on PyPi, so you can install it using you package manager of choice, for example:

```bash
pip install osma
```

```bash
poetry add osma
```

## Setting up

OSMA sources and aggregators can be setup using a config file.

```toml
[aggregators]

    [aggregators.jekyll]
    type="JekyllCoverageAggregator"
    entry_location="_posts"
    last_post_dates_file_name="last_posts.json"
    
        [aggregators.jekyll.query]
            type="ANDQuery"
            keywords=["cute", "cats"]

[sources]
    [sources.twitter]
        type="TwitterSource"
        access_token=""
        access_token_secret=""
        consumer_key=""
        consumer_secret=""
        bearer_token=""
    
    [sources.reddit]
        type="RedditSource"
        client_id=""
        client_secret=""
        user_agent="0x4D44"

    [sources.news]
        type="NewsAPISource"
        api_key=""

```

Let's see what's going on in the config file. It's split into two main sections: ``[aggregators]`` and ``[sources]``.

### Aggregator setup

The `type` argument in `[aggregators.jekyll]` tells OSMA to use ``JekyllCoverageAggregator`` class for the aggregator.

The `entry_location` argument specifies a folder where we will be saving fetched entries.

The `last_post_dates_file_name` specifies a file where should the dates of last entries be saved.This file helps to only fetch entries that we have not yet fetched.


`[aggregators.jekyll.query]` section sets up a query we want to run against all sources.

The `type` argument sets the type of query we want to use, `ANDQuery` in this case.

The `keywords` argument is a list of keywords we want to query.

Because we are using `ANDQuery` as a type, we will get entries that contain both 'cute' and 'cats' as keywords, who wants to look at non-cute cats anyway.

### Sources setup

The `type` argument in the `[sources]` subsections tells OSMA which class of source to use.

Additional arguments are source-specific and specify API config values.

## Running

If we save the above file as `cats.toml` we can run OSMA using

```bash
osma -c cats.toml run
```

This should pass the query to each source one by one and save Jekyll posts into the `_posts` folder.