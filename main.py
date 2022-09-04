
import asyncio
from datetime import datetime
import logging
import optparse
from random import randint
import time
from typing import List
from core.discord import DiscordBot
from core.gql_client import GqlClient
from core.model import NetworkPerformance, RunnerPerformance
from core.tweet_utils import TwitterBot
from gql_requests import get_largest_nodes_runners_query, get_nodes_runners_perf, get_network_perf_query
from dotenv import load_dotenv
import csv

load_dotenv()

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
        results.append(data)
    return results


def get_stats(num_node_runners=25):
    logging.info(f'STARTING - pokt-explorer client')

    logging.info(f'Initializing Gql client')
    gql_client = GqlClient()

    # logging.info(f'Initializing Aws client')
    # aws_client = AwsClient()

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

    # sort by power of domain
    big_nodes_runners.get(
        'largestNodeRunners').get('items').sort(key=lambda x: x['tokens'], reverse=True)

    # only look at top 25 domains by tokens
    node_runners = dict((r['service_domain'], r['tokens']) for r in big_nodes_runners.get(
        'largestNodeRunners').get('items')[:num_node_runners])

    # TODO: Reenable when their server support parallel
    # runners_data = asyncio.run(
    #     download_runners_data_parallel(gql_client, node_runners))

    runners_data = asyncio.run(
        download_runners_data_sequential(gql_client, node_runners))
    if not runners_data:
        raise Exception(f'Could not fetch nodes runners data')

    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    domains = list(node_runners.keys())
    nodes_runners: List[RunnerPerformance] = []
    for i, r in enumerate(runners_data):
        response = r.get('getNodeRunnerSummary')
        service_domain = domains[i]
        tokens_by_15k = node_runners[service_domain] / 15e3 / 1e6
        if response:
            # aws_client.save_to_s3(
            #    bucket_file=f'pokt-stats/{get_nodes_runners_perf.GET_NODES_RUNNER_PERF_QUERY_ID}-[{node_runners[i]}]-{ts}.json', data=response)
            #logging.debug(f'Successfully saved runners data')
            rp = RunnerPerformance(
                runner_domain=service_domain,
                # total_last_48_hours=response.get('total_last_48_hours'),
                # total_last_24_hours=response.get('total_last_24_hours'),
                # total_last_6_hours=response.get('total_last_6_hours'),
                avg_last_48_hours=response.get(
                    'serviced_last_48_hours') / tokens_by_15k,
                avg_last_24_hours=response.get(
                    'serviced_last_24_hours') / tokens_by_15k,
                avg_last_6_hours=response.get(
                    'serviced_last_6_hours') / tokens_by_15k,
                # jailed_now=response.get('jailed_now'),
                total_chains=response.get('total_chains'),
                total_nodes=response.get('total_nodes'),
                tokens=node_runners[service_domain] / 1e6
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
            servicer = response.get('servicer')
            if servicer:
                net_perf = NetworkPerformance(
                    max_pokt=servicer.get('thirty_days_max_pokt_avg') / 1e6,
                    today_pokt=servicer.get(
                        'twenty_fours_hs_less_pokt_avg') / 1e6,
                    thirty_day_pokt_avg=servicer.get(
                        'thirty_days_max_pokt_avg') / 1e6,
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
        logging.info(f'====== Posting data to Twitter ======')
        tweepy_client.post_nodes_runners_perf(nodes_runner_perf, 24)
        tweepy_client.post_nodes_runners_perf(nodes_runner_perf, 48)


def Main():
    parser = optparse.OptionParser()

    parser.add_option('-n', '--num-node-runners', dest='num_node_runners',
                      default=3, type='int', help='Number of node runners to get stats for')

    parser.add_option('-d', '--discord', dest='discord',
                      default=False, action='store_true')

    parser.add_option('-t', '--tweet', dest='tweet',
                      default=False, action='store_true')

    (options, args) = parser.parse_args()

    netperf, runners_perf = get_stats(options.num_node_runners)

    # generate csv file
    keys = list(
        {k: v for k, v in runners_perf[0].dict().items() if v is not None}.keys())
    with open('node_runners.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows([{k: v for k, v in rp.dict(
        ).items() if v is not None} for rp in runners_perf])

    print([netperf])
    print(runners_perf)

    if(options.discord):
        post_discord_message(netperf, runners_perf)
    if(options.tweet):
        post_twitter_message(runners_perf)
    else:
        print(parser.usage)
    logging.info('Program complete exiting')
    exit(0)


if __name__ == '__main__':
    Main()
