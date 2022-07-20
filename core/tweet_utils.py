import enum
from typing import List

from pexpect import ExceptionPexpect
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

    def test_tweet(self, perf_avg=24):
        try:
            self.api.update_status(
                "This is a test tweet\nto the moon \U0001F680")
        except Exception as ex:
            logging.error(f'An error occurred when sending test tweet: {ex}')

    def post_nodes_runners_perf(self, runners_data: List[RunnerPerformance], perf_avg=24):

        def highlight_sendnodes(x, y): return str(
            x) + ":" + str(y) + " \U0001F680" if "sendnodes.org" in x.lower() else str(x) + ":" + str(y)
        if perf_avg == 24:
            runners_data.sort(key=lambda r: r.avg_last_24_hours, reverse=True)
            tweet = 'Top nodes runners 24h\n' + '\n'.join(
                [f'{highlight_sendnodes(r.runner_domain, round(r.avg_last_24_hours))}' for r in runners_data])
        elif perf_avg == 48:
            runners_data.sort(key=lambda r: r.avg_last_48_hours, reverse=True)
            tweet = 'Top nodes runners 48h \n' + '\n'.join(
                [f'{highlight_sendnodes(r.runner_domain, round(r.avg_last_48_hours))}' for r in runners_data])
        else:
            raise Exception('Can not resolve perf average')
        # If tweet is longer than 180 we need to shorten it
        TWEET_LIMIT = 180
        if len(tweet) > TWEET_LIMIT:
            logging.info(
                f'Current length is over {TWEET_LIMIT} shortening tweet')
            rows = tweet.split('\n')
            total_length = 0
            row_index = 0
            thread = []
            start_idx = 0
            while row_index < len(rows) - 1:
                while total_length + len(rows[row_index]) < TWEET_LIMIT:
                    total_length += len(rows[row_index])
                    if row_index == len(rows)-1:
                        break
                    else:
                        row_index += 1

                if start_idx > 0:
                    s_tweet = '\U0001F447\n' + \
                        '\n'.join(rows[start_idx:row_index])
                else:
                    s_tweet = '\n'.join(rows[start_idx:row_index])
                thread.append(s_tweet)
                total_length = 0
                start_idx = row_index

            try:
                for i, t in enumerate(thread):
                    if i == 0:
                        current_tweet = self.api.update_status(
                            t, auto_populate_reply_metadata=True)
                    else:
                        current_tweet = self.api.update_status(
                            t, in_reply_to_status_id=current_tweet.id, auto_populate_reply_metadata=True)
            except Exception as ex:
                logging.error(
                    f'An error occurred when sending performance tweet: {ex}')
                raise
        else:
            try:
                self.api.update_status(t, auto_populate_reply_metadata=True)
            except Exception as ex:
                logging.error(
                    f'An error occurred when sending performance tweet: {ex}')
                raise
