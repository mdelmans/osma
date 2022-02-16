# Welcome to OSMA

OSMA stands for Open Social Media Aggregator. It combines APIs of most common social media platforms and allows you to query multiple sources at once for new entries.

Currently, OSMA uses the following social media APIs:

* Twitter using [tweepy](https://www.tweepy.org/)
* Reddit using [praw](https://praw.readthedocs.io/en/stable/)
* NewsAPI using [newsapi](https://newsapi.org/docs/client-libraries/python)

You can easily extend OSMA to use other APIs, check out [Add a new source] on how to do it.

At the moment, OSMA only supports [Jekyll](https://jekyllrb.com/) as an aggregator frontend. But you can easily add your own. See [Add a new aggregator] on how to do it.

See OSMA documentation for more details.

## Contributing

This is a small side-project but contributions are welcome, especially if you are adding a new Source or Aggregator class.