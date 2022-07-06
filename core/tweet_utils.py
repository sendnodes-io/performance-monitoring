from typing import List
from core import utils
import logging
import tweepy
from core import constants as cst
from core.model import RunnerPerformance


class TwitterBot():
    def __init__(self) -> None:
        env_var = utils.get_env_variables(
            [
                cst.TWITTER_API_KEY,
                cst.TWITTER_API_SECRET,
                cst.TWITTER_ACCESS_TOKEN,
                cst.TWITTER_ACCESS_TOKEN_SECRET
            ]
        )
        auth = tweepy.OAuthHandler(env_var.get(cst.TWITTER_API_KEY),
                                   env_var.get(cst.TWITTER_API_SECRET))

        auth.set_access_token(env_var.get(cst.TWITTER_ACCESS_TOKEN),
                              env_var.get(cst.TWITTER_ACCESS_TOKEN_SECRET))

        api = tweepy.API(auth,
                         wait_on_rate_limit=True,
                         retry_count=10,
                         retry_delay=5)
        try:
            api.verify_credentials()
            logging.debug(f'Twitter bot authenticated successfully')
            self.api = api
        except Exception as ex:
            logging.fatal(f'Could not initialize twitter client: {ex}')
            raise

    def test_tweet(self):
        try:
            self.api.update_status(
                "This is a test tweet\nto the moon \U0001F680")
        except Exception as ex:
            logging.error(f'An error occurred when sending test tweet: {ex}')

    def post_nodes_runners_perf(self, runners_data: List[RunnerPerformance]):
        runners_data.sort(key=lambda r: r.avg_last_24_hours, reverse=True)

        def highlight_sendnodes(x): str(
            x) + " \U0001F680" if "sendnodes.org" in x.lower() else str(x)
        tweet = '\n'.join(
            [f'{highlight_sendnodes(r.runner_domain)}:{round(r.avg_last_48_hours)}' for r in runners_data])

        # If tweet is longer than 280 we need to shorten it
        if len(tweet) > 280:
            logging.info(f'Current length is over 280 shortening tweet')
            rows = tweet.split('\n')
            total_length = 0
            row_index = 0
            while total_length + len(rows[row_index]) < 280:
                total_length += len(rows[row_index])
                row_index += 1
            tweet = '\n'.join(rows[:row_index])

        try:
            self.api.update_status(tweet)
        except Exception as ex:
            logging.error(
                f'An error occurred when sending performance tweet: {ex}')
            raise
