python-tweet-moods
=====

Uses [Tweepy Streaming API](http://docs.tweepy.org/en/v3.4.0/streaming_how_to.html) with access-tokens for a registered Twitter application to read tweets containing the string "python". Then uses the Naive Bayesian sentiment analyzer from [TextBlob](https://textblob.readthedocs.org/en/dev/) to gauge whether the tweet is considered positive or negative. Results are sent to [Hosted Graphite](http://hostedgraphite.com) every 3 minutes.

## Dependencies
    $ pip install -U tweepy
    $ pip install -U textblob

## Running
    $ python stream.py