
import asyncio
from datetime import datetime
import logging
import optparse
from random import randint
import time
from typing import List
from core.discord import DiscordBot
from core.gql_client import GqlClient
from core.aws_utils import AwsClient
from core.model import NetworkPerformance, RunnerPerformance
from core.tweet_utils import TwitterBot
from gql_requests import get_largest_nodes_runners_query, get_nodes_runners_perf, get_network_perf_query

# Initialise logger
logging.basicConfig(level=logging.INFO,
                    format='%(name)s - %(levelname)s - %(message)s')


async def download_runners_data_parallel(gql_client, runners_domains):
    logging.info('Getting average perf for top node runners')
    tasks = []

    for r in runners_domains:
        task = asyncio.ensure_future(gql_client.send_query(get_nodes_runners_perf.GET_NODES_RUNNER_PERF_QUERY,
                                     get_nodes_runners_perf.GET_NODES_RUNNER_PERF_QUERY_ID, {"domain": r}))
        tasks.append(task)
    await asyncio.gather(*tasks, return_exceptions=True)
    return tasks


async def download_runners_data_sequential(gql_client, runners_domains):
    logging.info('Getting average perf for top node runners')
    results = []
    for r in runners_domains:
        data = await gql_client.send_query(get_nodes_runners_perf.GET_NODES_RUNNER_PERF_QUERY,
                                           get_nodes_runners_perf.GET_NODES_RUNNER_PERF_QUERY_ID + f"[{r}]", {"domain": r})
        time.sleep(randint(10, 20))
        results.append(data)
    return results


def get_stats():
    logging.info(f'STARTING - pokt-explorer client')

    logging.info(f'Initializing Gql client')
    gql_client = GqlClient()

    logging.info(f'Initializing Aws client')
    aws_client = AwsClient()

    logging.info('====== Data collection phase ======')
    logging.info('Getting biggest runners data')
    big_nodes_runners = asyncio.run(gql_client.send_query(
        get_largest_nodes_runners_query.GET_LARGEST_NODES_RUNNERS_QUERY,
        get_largest_nodes_runners_query.GET_LARGEST_NODES_RUNNERS_QUERY_ID)
    )
    if not big_nodes_runners:
        logging.warn('Skipping saving big nodes runners no data returned')
        raise Exception(
            f'Could not retrieve big nodes runners exiting - will improve soon')

    runners_names = [r['service_domain'] for r in big_nodes_runners.get(
        'largestNodeRunners').get('items')]

    # TODO: Reenable when their server support parallel
    # runners_data = asyncio.run(
    #     download_runners_data_parallel(gql_client, runners_names))

    runners_data = asyncio.run(
        download_runners_data_sequential(gql_client, runners_names))
    if not runners_data:
        raise Exception(f'Could not fetch nodes runners data')

    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    nodes_runners: List[RunnerPerformance] = []
    for i, r in enumerate(runners_data):
        response = r.get('getNodeRunnerSummary')
        if response:
            aws_client.save_to_s3(
                bucket_file=f'pokt-stats/{get_nodes_runners_perf.GET_NODES_RUNNER_PERF_QUERY_ID}-[{runners_names[i]}]-{ts}.json', data=response)
            logging.debug(f'Successfully saved runners data')
            rp = RunnerPerformance(
                runner_domain=runners_names[i],
                total_last_48_hours=response.get('total_last_48_hours'),
                total_last_24_hours=response.get('total_last_24_hours'),
                total_last_6_hours=response.get('total_last_6_hours'),
                avg_last_48_hours=response.get('avg_last_48_hours'),
                avg_last_24_hours=response.get('avg_last_24_hours'),
                avg_last_6_hours=response.get('avg_last_6_hours'),
                jailed_now=response.get('jailed_now'),
                total_chains=response.get('total_chains'),
                total_nodes=response.get('total_nodes'),
                total_balance=response.get('total_balance'),
            )
            nodes_runners.append(rp)

    network_performance = asyncio.run(gql_client.send_query(
        get_network_perf_query.GET_NETWORK_PERFORMANCE_QUERY,
        get_network_perf_query.GET_NETWORK_PERFORMANCE_QUERY_ID
    ))
    if not network_performance:
        logging.error(f'Could not fetch data for network perf.')
    else:
        response = network_performance.get('getPoktEarnPerformance')
        if response:
            net_perf = NetworkPerformance(
                max_pokt=response.get('max_pokt'),
                today_pokt=response.get('today_pokt'),
                thirty_day_pokt_avg=response.get('thirty_day_pokt_avg'),
            )
    return net_perf, nodes_runners


def post_discord_message(network_performance: NetworkPerformance,
                         nodes_runners_perf: List[RunnerPerformance]):
    logging.info(f'Initializing Discord client')
    discord_client = DiscordBot()

    logging.info(f'====== Posting data to Discord ======')
    if(network_performance):
        discord_client.post_network_perf_data(network_performance)
    if(nodes_runners_perf):
        discord_client.post_runners_perf_data(nodes_runners_perf)


def post_twitter_message(nodes_runner_perf: List[RunnerPerformance]):
    logging.info(f'Initializing Twitter Bot')
    tweepy_client = TwitterBot()
    if nodes_runner_perf:
        tweepy_client.post_nodes_runners_perf(nodes_runner_perf)


def Main():
    parser = optparse.OptionParser()

    parser.add_option('-d', '--discord', dest='discord',
                      default=False, action='store_true')

    parser.add_option('-t', '--tweet', dest='tweet',
                      default=False, action='store_true')

    (options, args) = parser.parse_args()

    netperf, runners_perf = get_stats()
    if(options.discord):
        post_discord_message(netperf, runners_perf)
    if(options.tweet):
        post_twitter_message(runners_perf)
    else:
        print(parser.usage)
    exit(0)


if __name__ == '__main__':
    Main()
