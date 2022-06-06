
import asyncio
import logging
from random import randint
from sys import dont_write_bytecode
import time
from typing import List
from unittest import result, runner
from core.discord import DiscordBot
from core.gql_client import GqlClient
from core.aws_utils import AwsClient
from core.model import RunnerPerformance
from gql_requests import get_largest_nodes_runners_query, get_nodes_runners_perf

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

if __name__ == '__main__':
    logging.info(f'STARTING - pokt-explorer client')

    logging.info(f'Initializing Gql client')
    gql_client = GqlClient()

    logging.info(f'Initializing Aws client')
    aws_client = AwsClient()

    logging.info(f'Initializing Discord client')
    discord_client = DiscordBot()

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

    logging.info('Persisting nodes runners information to AWS')

    aws_client.save_to_s3(
        bucket_file=f'pokt-stats/{get_largest_nodes_runners_query.GET_LARGEST_NODES_RUNNERS_QUERY_ID}.json', data=big_nodes_runners)
    logging.debug('Successfully saved big nodes runners into S3')

    runners_names = [r['service_domain'] for r in big_nodes_runners.get(
        'largestNodeRunners').get('items')]
    runners_names.append("sendnodes.io")

    # TODO: Reenable when their server support parallel
    # runners_data = asyncio.run(
    #     download_runners_data_parallel(gql_client, runners_names))

    runners_data = asyncio.run(
        download_runners_data_sequential(gql_client, runners_names))
    if not runners_data:
        raise Exception(f'Could not fetch nodes runners data')

    nodes_runners: List[RunnerPerformance] = []
    for i, r in enumerate(runners_data):
        response = r.get('getNodeRunnerSummary')
        if response:
            aws_client.save_to_s3(
                bucket_file=f'pokt-stats/{get_nodes_runners_perf.GET_NODES_RUNNER_PERF_QUERY_ID}-[{runners_names[i]}].json', data=response)
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

        discord_client.post_runners_perf_data(nodes_runners)
