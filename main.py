from dotenv import load_dotenv

load_dotenv()

import constants
import asyncio
from datetime import datetime, timedelta
import logging
import optparse
from typing import List
import core.db
from core.discord import DiscordBot
from core.gql_client import GqlClient
from core.model import (
    ChainReward,
    ChainRewardOrm,
    NetworkPerformance,
    RunnerPerformance,
    RunnerPerformanceOrm,
)
from core.tweet_utils import TwitterBot
from gql_requests import (
    get_largest_nodes_runners_query,
    get_nodes_runners_perf,
    get_network_perf_query,
    get_chain_rewards_query,
)
import csv
from sqlalchemy.orm import Session


# Initialise logger
logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")


async def download_runners_data_parallel(gql_client, runners_domains):
    logging.info("Getting average perf for top node runners")
    tasks = []

    for r in runners_domains:
        task = asyncio.ensure_future(
            gql_client.send_query(
                get_nodes_runners_perf.GET_NODES_RUNNER_PERF_QUERY,
                get_nodes_runners_perf.GET_NODES_RUNNER_PERF_QUERY_ID,
                {"domain": r},
            )
        )
        tasks.append(task)
    await asyncio.gather(*tasks, return_exceptions=True)
    return tasks


async def download_runners_data_sequential(gql_client, runners_domains):
    logging.info("Getting average perf for top node runners")
    results = []
    for r in runners_domains:
        data = await gql_client.send_query(
            get_nodes_runners_perf.GET_NODES_RUNNER_PERF_QUERY,
            get_nodes_runners_perf.GET_NODES_RUNNER_PERF_QUERY_ID + f"[{r}]",
            {"domain": r},
        )
        results.append(data)
    return results


def get_stats(num_node_runners=25):
    logging.info(f"STARTING - pokt-explorer client")

    logging.info(f"Initializing Gql client")
    gql_client = GqlClient()

    # logging.info(f'Initializing Aws client')
    # aws_client = AwsClient()

    logging.info("====== Data collection phase ======")
    logging.info("Getting biggest runners data")
    big_nodes_runners_response = asyncio.run(
        gql_client.send_query(
            get_largest_nodes_runners_query.GET_LARGEST_NODES_RUNNERS_QUERY,
            get_largest_nodes_runners_query.GET_LARGEST_NODES_RUNNERS_QUERY_ID,
        )
    )
    if not big_nodes_runners_response:
        logging.warning("Skipping saving big nodes runners no data returned")
        raise Exception(
            f"Could not retrieve big nodes runners exiting - will improve soon"
        )

    big_nodes_runners = big_nodes_runners_response.get("ListLargestNodeRunners").get(
        "items"
    )

    # sort by power of domain
    big_nodes_runners.sort(key=lambda x: x["tokens"], reverse=True)

    # only look at top 25 domains by tokens
    node_runners = dict(
        (r["service_domain"], r["tokens"]) for r in big_nodes_runners[:num_node_runners]
    )

    # include hard-coded domains
    hard_coded_domains = ["aapokt.com", "cryptonode.tools", "qspider.com"]
    for domain in hard_coded_domains:
        node_runner = next(
            (r for r in big_nodes_runners if r["service_domain"] == domain), None
        )
        node_runners[domain] = node_runner["tokens"] if node_runner else 0

    # TODO: Reenable when their server support parallel
    # runners_data = asyncio.run(
    #     download_runners_data_parallel(gql_client, node_runners))

    runners_data = asyncio.run(
        download_runners_data_sequential(gql_client, node_runners)
    )
    if not runners_data:
        raise Exception(f"Could not fetch nodes runners data")

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    domains = list(node_runners.keys())
    nodes_runners: List[RunnerPerformance] = []
    for i, r in enumerate(runners_data):
        node_runner_summ = r.get("GetSummaryForNodeSelection")
        service_domain = domains[i]
        if node_runner_summ:
            validator_nodes = node_runner_summ.get("validators")
            validator_tokens_pokt = (
                node_runner_summ.get("validators_tokens_staked") / constants.UPOKT_DENOM
            )
            all_tokens_staked_pokt = (
                node_runner_summ.get("total_tokens_staked") / constants.UPOKT_DENOM
            )
            num_of_15k_pokt_nodes = servicer_node_summary(
                validator_nodes, validator_tokens_pokt, all_tokens_staked_pokt
            )

            # aws_client.save_to_s3(
            #    bucket_file=f'pokt-stats/{get_nodes_runners_perf.GET_NODES_RUNNER_PERF_QUERY_ID}-[{node_runners[i]}]-{ts}.json', data=response)
            # logging.debug(f'Successfully saved runners data')
            rp = RunnerPerformance(
                runner_domain=service_domain,
                relays_last_48_hours=node_runner_summ.get("relays_last_48hrs"),
                relays_last_24_hours=node_runner_summ.get("relays_last_24hrs"),
                relays_last_6_hours=node_runner_summ.get("relays_last_6hrs"),
                serviced_last_48_hours=node_runner_summ.get(
                    "servicer_rewards_last_48hrs"
                )
                / constants.UPOKT_DENOM,
                serviced_last_24_hours=node_runner_summ.get(
                    "servicer_rewards_last_24hrs"
                )
                / constants.UPOKT_DENOM,
                serviced_last_6_hours=node_runner_summ.get("servicer_rewards_last_6hrs")
                / constants.UPOKT_DENOM,
                producer_rewards_last_48_hours=node_runner_summ.get(
                    "producer_rewards_last_48hrs"
                )
                / constants.UPOKT_DENOM,
                producer_rewards_last_24_hours=node_runner_summ.get(
                    "producer_rewards_last_24hrs"
                )
                / constants.UPOKT_DENOM,
                producer_rewards_last_6_hours=node_runner_summ.get(
                    "producer_rewards_last_6hrs"
                )
                / constants.UPOKT_DENOM,
                total_last_48_hours=node_runner_summ.get("total_rewards_last_48hrs")
                / constants.UPOKT_DENOM,
                total_last_24_hours=node_runner_summ.get("total_rewards_last_24hrs")
                / constants.UPOKT_DENOM,
                total_last_6_hours=node_runner_summ.get("total_rewards_last_6hrs")
                / constants.UPOKT_DENOM,
                avg_relays_last_48_hours=node_runner_summ.get("avg_relays_last_48hrs"),
                avg_relays_last_24_hours=node_runner_summ.get("avg_relays_last_24hrs"),
                avg_relays_last_6_hours=node_runner_summ.get("avg_relays_last_6hrs"),
                avg_last_48_hours=node_runner_summ.get("servicer_rewards_last_48hrs")
                / num_of_15k_pokt_nodes
                / constants.UPOKT_DENOM,
                avg_last_24_hours=node_runner_summ.get("servicer_rewards_last_24hrs")
                / num_of_15k_pokt_nodes
                / constants.UPOKT_DENOM,
                avg_last_6_hours=node_runner_summ.get("servicer_rewards_last_6hrs")
                / num_of_15k_pokt_nodes
                / constants.UPOKT_DENOM,
                avg_base_last_48_hours=node_runner_summ.get(
                    "avg_base_servicer_rewards_last_48hrs"
                )
                / constants.UPOKT_DENOM,
                avg_base_last_24_hours=node_runner_summ.get(
                    "avg_base_servicer_rewards_last_24hrs"
                )
                / constants.UPOKT_DENOM,
                avg_base_last_6_hours=node_runner_summ.get(
                    "avg_base_servicer_rewards_last_6hrs"
                )
                / constants.UPOKT_DENOM,
                avg_total_last_48_hours=node_runner_summ.get(
                    "avg_total_rewards_last_48hrs"
                )
                / constants.UPOKT_DENOM,
                avg_total_last_24_hours=node_runner_summ.get(
                    "avg_total_rewards_last_24hrs"
                )
                / constants.UPOKT_DENOM,
                avg_total_last_6_hours=node_runner_summ.get(
                    "avg_total_rewards_last_6hrs"
                )
                / constants.UPOKT_DENOM,
                avg_producer_last_48_hours=node_runner_summ.get(
                    "avg_producer_rewards_last_48hrs"
                )
                / constants.UPOKT_DENOM,
                avg_producer_last_24_hours=node_runner_summ.get(
                    "avg_producer_rewards_last_24hrs"
                )
                / constants.UPOKT_DENOM,
                avg_producer_last_6_hours=node_runner_summ.get(
                    "avg_producer_rewards_last_6hrs"
                )
                / constants.UPOKT_DENOM,
                producer_times_last_48_hours=node_runner_summ.get(
                    "producer_times_last_48hrs"
                ),
                producer_times_last_24_hours=node_runner_summ.get(
                    "producer_times_last_24hrs"
                ),
                producer_times_last_6_hours=node_runner_summ.get(
                    "producer_times_last_6hrs"
                ),
                total_tokens_staked=all_tokens_staked_pokt,
                total_validator_tokens_staked=validator_tokens_pokt,
                validators=node_runner_summ.get("validators"),
                last_height=node_runner_summ.get("last_height"),
                total_pending_relays=node_runner_summ.get("total_pending_relays"),
                total_estimated_pending_rewards=node_runner_summ.get(
                    "total_estimated_pending_rewards"
                ),
                total_chains=node_runner_summ.get("total_chains"),
                jailed_now=node_runner_summ.get("jailed_now"),
                total_balance=node_runner_summ.get("total_balance")
                / constants.UPOKT_DENOM,
                total_output_balance=node_runner_summ.get("total_output_balance")
                / constants.UPOKT_DENOM,
                total_nodes=node_runner_summ.get("total_nodes"),
                nodes_staked=node_runner_summ.get("nodes_staked"),
                nodes_unstaked=node_runner_summ.get("nodes_unstaked"),
                nodes_unstaking=node_runner_summ.get("nodes_unstaking"),
                tokens=all_tokens_staked_pokt,
            )
            nodes_runners.append(rp)

    # save to db
    with Session(core.db.ENGINE) as session:
        for runner in nodes_runners:
            session.merge(
                RunnerPerformanceOrm(
                    runner_domain=runner.runner_domain,
                    relays_last_48_hours=runner.relays_last_48_hours,
                    relays_last_24_hours=runner.relays_last_24_hours,
                    relays_last_6_hours=runner.relays_last_6_hours,
                    serviced_last_48_hours=runner.serviced_last_48_hours,
                    serviced_last_24_hours=runner.serviced_last_24_hours,
                    serviced_last_6_hours=runner.serviced_last_6_hours,
                    producer_rewards_last_48_hours=runner.producer_rewards_last_48_hours,
                    producer_rewards_last_24_hours=runner.producer_rewards_last_24_hours,
                    producer_rewards_last_6_hours=runner.producer_rewards_last_6_hours,
                    total_last_48_hours=runner.total_last_48_hours,
                    total_last_24_hours=runner.total_last_24_hours,
                    total_last_6_hours=runner.total_last_6_hours,
                    avg_relays_last_48_hours=runner.avg_relays_last_48_hours,
                    avg_relays_last_24_hours=runner.avg_relays_last_24_hours,
                    avg_relays_last_6_hours=runner.avg_relays_last_6_hours,
                    avg_last_48_hours=runner.avg_last_48_hours,
                    avg_last_24_hours=runner.avg_last_24_hours,
                    avg_last_6_hours=runner.avg_last_6_hours,
                    avg_base_last_48_hours=runner.avg_base_last_48_hours,
                    avg_base_last_24_hours=runner.avg_base_last_24_hours,
                    avg_base_last_6_hours=runner.avg_base_last_6_hours,
                    avg_total_last_48_hours=runner.avg_total_last_48_hours,
                    avg_total_last_24_hours=runner.avg_total_last_24_hours,
                    avg_total_last_6_hours=runner.avg_total_last_6_hours,
                    avg_producer_last_48_hours=runner.avg_producer_last_48_hours,
                    avg_producer_last_24_hours=runner.avg_producer_last_24_hours,
                    avg_producer_last_6_hours=runner.avg_producer_last_6_hours,
                    producer_times_last_48_hours=runner.producer_times_last_48_hours,
                    producer_times_last_24_hours=runner.producer_times_last_24_hours,
                    producer_times_last_6_hours=runner.producer_times_last_6_hours,
                    total_tokens_staked=runner.total_tokens_staked,
                    total_validator_tokens_staked=runner.total_validator_tokens_staked,
                    validators=runner.validators,
                    last_height=runner.last_height,
                    total_pending_relays=runner.total_pending_relays,
                    total_estimated_pending_rewards=runner.total_estimated_pending_rewards,
                    total_chains=runner.total_chains,
                    jailed_now=runner.jailed_now,
                    total_balance=runner.total_balance,
                    total_output_balance=runner.total_output_balance,
                    total_nodes=runner.total_nodes,
                    nodes_staked=runner.nodes_staked,
                    nodes_unstaked=runner.nodes_unstaked,
                    nodes_unstaking=runner.nodes_unstaking,
                    tokens=runner.tokens,
                    created_at=datetime.now(),
                )
            )
        session.commit()

    network_performance = asyncio.run(
        gql_client.send_query(
            get_network_perf_query.GET_NETWORK_PERFORMANCE_QUERY,
            get_network_perf_query.GET_NETWORK_PERFORMANCE_QUERY_ID,
        )
    )
    if not network_performance:
        logging.error(f"Could not fetch data for network perf.")
    else:
        node_runner_summ = network_performance.get("GetNetworkEarnPerformanceReport")
        if node_runner_summ:
            servicer = node_runner_summ.get("servicer")
            if servicer:
                net_perf = NetworkPerformance(
                    max_pokt=servicer.get("thirty_days_max_pokt_avg")
                    / constants.UPOKT_DENOM,
                    today_pokt=servicer.get("twenty_fours_hs_less_pokt_avg")
                    / constants.UPOKT_DENOM,
                    thirty_day_pokt_avg=servicer.get("thirty_days_max_pokt_avg")
                    / constants.UPOKT_DENOM,
                )

    chain_rewards = get_chains_rewards(gql_client)

    return net_perf, nodes_runners, chain_rewards


# calculate number of 15k POKT servicer nodes using:
# (Total tokens staked - (Total Validator Tokens - (Total Validator Nodes * 60k))) / 15k
def servicer_node_summary(
    validator_nodes, validator_tokens_pokt, all_tokens_staked_pokt
):
    validator_tokens_excess_pokt = (
        validator_tokens_pokt - validator_nodes * constants.POKT_NODE_MAX
    )
    num_of_15k_pokt_nodes = (
        all_tokens_staked_pokt - validator_tokens_excess_pokt
    ) / constants.POKT_NODE_MIN
    return num_of_15k_pokt_nodes


def post_discord_message(
    network_performance: NetworkPerformance,
    nodes_runners_perf: List[RunnerPerformance],
    chain_rewards: List[ChainReward],
):
    logging.info(f"Initializing Discord client")
    discord_client = DiscordBot()

    logging.info(f"====== Posting data to Discord ======")
    if network_performance:
        discord_client.post_network_perf_data(network_performance)
    if chain_rewards:
        discord_client.post_chain_rewards_data(chain_rewards)
    if nodes_runners_perf:
        discord_client.post_runners_perf_data(nodes_runners_perf)


def post_twitter_message(nodes_runner_perf: List[RunnerPerformance]):
    logging.info(f"Initializing Twitter Bot")
    tweepy_client = TwitterBot()
    if nodes_runner_perf:
        logging.info(f"====== Posting data to Twitter ======")
        tweepy_client.post_nodes_runners_perf(nodes_runner_perf, 24)
        tweepy_client.post_nodes_runners_perf(nodes_runner_perf, 48)


def get_chains_rewards(gql_client: GqlClient):
    # get chain rewards data
    start = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S") + "Z"
    end = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + "Z"
    chain_rewards = asyncio.run(
        gql_client.send_query(
            get_chain_rewards_query.GET_CHAINS_REWARDS_BETWEEN_DATES,
            get_chain_rewards_query.GET_CHAINS_REWARDS_BETWEEN_DATES_QUERY_ID,
            {"start": start, "end": end, "format": "YYYY-MM-DDTHH:mm:ssZ"},
        )
    )
    if not chain_rewards:
        logging.error(f"Could not fetch data for chain rewards.")
        return []

    chain_rewards = chain_rewards.get("GetChainsRewardsBetweenDates")
    if not chain_rewards:
        logging.error(f"No chain rewards data in the response.")
        return []

    logging.info(f"====== Chain Rewards ======")
    print(chain_rewards)

    chain_reward_models = []
    with Session(core.db.ENGINE) as session:
        for reward in chain_rewards:
            chain_reward_orm = ChainRewardOrm(
                chain=reward["chain"],
                total_relays=reward["total_relays"],
                total_pokt=reward["total_pokt"],
                staked_nodes_avg=reward["staked_nodes_avg"],
                pokt_avg=reward["pokt_avg"],
                relays_avg=reward["relays_avg"],
                created_at=datetime.utcnow(),
            )

            session.merge(chain_reward_orm)

            chain_reward_model = ChainReward(
                chain=reward["chain"],
                total_relays=reward["total_relays"],
                total_pokt=reward["total_pokt"],
                staked_nodes_avg=reward["staked_nodes_avg"],
                pokt_avg=reward["pokt_avg"],
                relays_avg=reward["relays_avg"],
            )

            chain_reward_models.append(chain_reward_model)

        session.commit()

    return chain_reward_models


def Main():
    parser = optparse.OptionParser()

    parser.add_option(
        "-n",
        "--num-node-runners",
        dest="num_node_runners",
        default=3,
        type="int",
        help="Number of node runners to get stats for",
    )

    parser.add_option(
        "-d", "--discord", dest="discord", default=False, action="store_true"
    )

    parser.add_option("-t", "--tweet", dest="tweet", default=False, action="store_true")

    (options, args) = parser.parse_args()

    netperf, runners_perf, chains_rewards = get_stats(options.num_node_runners)

    # generate csv file
    keys = list(
        {k: v for k, v in runners_perf[0].dict().items() if v is not None}.keys()
    )
    with open("node_runners.csv", "w", newline="") as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(
            [
                {k: v for k, v in rp.dict().items() if v is not None}
                for rp in runners_perf
            ]
        )

    print([netperf])
    print(runners_perf)
    print(chains_rewards)

    if options.discord:
        post_discord_message(netperf, runners_perf, chains_rewards)
    if options.tweet:
        post_twitter_message(runners_perf)
    else:
        print(parser.usage)
    logging.info("Program complete exiting")
    exit(0)


if __name__ == "__main__":
    Main()
