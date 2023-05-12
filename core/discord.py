import json
import logging

import requests
import constants
from typing import List
from unittest import runner
from core import utils
from core import constants as cst
from discord_webhook import DiscordEmbed, DiscordWebhook
from core.model import ChainReward, NetworkPerformance, RunnerPerformance
import os.path
from tabulate import tabulate
import time
import decimal


class DiscordBot:
    def __init__(self) -> None:
        env_var = utils.get_env_variables([cst.DISCORD_WEBHOOK])
        self.discord_hook = env_var.get(cst.DISCORD_WEBHOOK)
        self.webhook = DiscordWebhook(
            url=env_var.get(cst.DISCORD_WEBHOOK),
            username="Perf Bot",
            rate_limit_retry=True,
        )

    def post_network_perf_data(self, network_data: NetworkPerformance):
        description = f"Today Pokt: {network_data.today_pokt}\n30d avg Pokt: {network_data.thirty_day_pokt_avg}"
        embed_net_perf = DiscordEmbed(
            title=f"Network Perf", description=f"{description}", color="ffb0e3"
        )
        self.webhook.remove_embeds()
        self.webhook.add_embed(embed_net_perf)
        self.webhook.execute()
        self.webhook.remove_embeds()

    def post_runners_perf_data(self, runners_data: List[RunnerPerformance]):
        # chuncks = [runners_data[x:x+9] for x in range(0, len(runners_data), 9)]
        self.webhook.remove_embeds()
        runners_data.sort(key=lambda r: (r.avg_last_48_hours,), reverse=True)
        # description = tabulate(
        #     [[r.runner_domain, f'{round(r.avg_last_48_hours, 3)}'] for r in runners_data], ["domain", "Average 48h"], maxcolwidths=[19, 9])
        description = "\n".join(
            [
                f"{r.runner_domain}:" + f"{round(r.avg_last_48_hours, 3)}"
                for r in runners_data
            ]
        )
        embed_48 = DiscordEmbed(
            title=f"Average 48h", description=f"{description}", color="03b2f8"
        )
        self.webhook.add_embed(embed_48)
        # self.webhook.content = f'```{description}```'
        self.webhook.execute()
        # time.sleep(2)
        self.webhook.remove_embeds()

        # Last 24 hours
        runners_data.sort(key=lambda r: (r.avg_last_24_hours,), reverse=True)
        # description = tabulate(
        #     [[r.runner_domain, f'{round(r.avg_last_24_hours, 3)}'] for r in runners_data], ["domain", "Average 24h"], maxcolwidths=[19, 9])
        description = "\n".join(
            [
                f"{r.runner_domain}:" + f"{round(r.avg_last_24_hours, 3)}"
                for r in runners_data
            ]
        )
        embed_24 = DiscordEmbed(
            title=f"Average 24h", description=f"{description}", color="66ff66"
        )
        self.webhook.add_embed(embed_24)
        # self.webhook.content = f'```{description}```'
        self.webhook.execute()
        # time.sleep(2)
        self.webhook.remove_embeds()

        # Last 6 hours
        runners_data.sort(key=lambda r: (r.avg_last_6_hours,), reverse=True)
        # description = tabulate(
        #     [[r.runner_domain, f'{round(r.avg_last_6_hours, 3)}'] for r in runners_data], ["domain", "Average 6h"], maxcolwidths=[19, 9])
        description = "\n".join(
            [
                f"{r.runner_domain}:" + f"{round(r.avg_last_6_hours, 3)}"
                for r in runners_data
            ]
        )
        embed_6 = DiscordEmbed(
            title=f"Average 6h", description=f"{description}", color="7d7d73"
        )
        self.webhook.add_embed(embed_6)
        # self.webhook.content = f'```{description}```'
        self.webhook.execute()
        # time.sleep(2)
        self.webhook.remove_embeds()

        # Chains count
        runners_data.sort(key=lambda r: (r.total_chains,), reverse=True)
        # description = tabulate(
        #     [[r.runner_domain, f'{r.total_chains:,}'] for r in runners_data], ["domain", "# chains"], colalign=("left", "right"), maxcolwidths=[19, 9])
        description = "\n".join(
            [f"{r.runner_domain}:" + f"{r.total_chains:,}" for r in runners_data]
        )
        embed_c = DiscordEmbed(
            title=f"# chains", description=f"{description}", color="ffff00"
        )
        self.webhook.add_embed(embed_c)
        # self.webhook.content = f'```{description}```'
        self.webhook.execute()
        # time.sleep(2)
        self.webhook.remove_embeds()

        # Nodes count
        runners_data.sort(key=lambda r: (r.nodes_staked,), reverse=True)
        # description = tabulate(
        #     [[r.runner_domain, f'{r.nodes_staked:,}'] for r in runners_data], ["domain", "# nodes"], colalign=("left", "right"), maxcolwidths=[19, 9])
        description = "\n".join(
            [f"{r.runner_domain}:" + f"{r.nodes_staked:,}" for r in runners_data]
        )
        embed_n = DiscordEmbed(
            title=f"# nodes", description=f"{description}", color="ff66ff"
        )
        self.webhook.add_embed(embed_n)
        # self.webhook.content = f'```{description}```'
        self.webhook.execute()
        # time.sleep(2)
        self.webhook.remove_embeds()

        # Total tokens
        runners_data.sort(key=lambda r: (r.tokens,), reverse=True)
        # description = tabulate(
        #     [[r.runner_domain, f'{round(r.tokens):,}'] for r in runners_data], ["domain", "# tokens"], colalign=("left", "right"), maxcolwidths=[19, 9])
        description = "\n".join(
            [f"{r.runner_domain}:" + f"{round(r.tokens):,}" for r in runners_data]
        )
        embed_n = DiscordEmbed(
            title=f"# tokens", description=f"{description}", color="6a0dad"
        )
        self.webhook.add_embed(embed_n)
        # self.webhook.content = f'```{description}```'
        self.webhook.execute()
        # time.sleep(2)
        self.webhook.remove_embeds()

        # add csv dump if exists
        if os.path.isfile("node_runners.csv"):
            with open("node_runners.csv", "rb") as f:
                self.webhook.add_file(file=f.read(), filename="node_runners.csv")

        self.webhook.execute()
        # time.sleep(2)

        # logging.info(response)

    def post_chain_rewards_data(self, chain_rewards_data: List[ChainReward]):
        # Sort the data
        chain_rewards_data.sort(key=lambda r: r.pokt_avg, reverse=True)

        # Select the top 25 chains
        top_chains = chain_rewards_data[:25]

        pokt_chains_map = {}
        try:
            # try https://poktscan-v1.nyc3.digitaloceanspaces.com/pokt-chains-map.json
            pokt_chains_map = requests.get(
                "https://poktscan-v1.nyc3.digitaloceanspaces.com/pokt-chains-map.json"
            ).json()
        except Exception as e:
            logging.error("Error fetching pokt-chains-map.json from poktscan", e)

        # Load pokt-chains-map.json from local file as fallback
        if not pokt_chains_map:
            with open("../pokt-chains-map.json", "r") as f:
                pokt_chains_map = json.load(f)

        # Prepare data for tabulate
        tabulated_data = [
            [
                pokt_chains_map.get(r.chain, {"label": r.chain})["label"],
                round(r.pokt_avg / decimal.Decimal(constants.UPOKT_DENOM), 2),
                f"{round(r.staked_nodes_avg):,}",
                f"{round(r.total_relays):,}",
            ]
            for r in top_chains
        ]

        # Create table using tabulate
        table = tabulate(
            tabulated_data,
            headers=["Chain", "Earn Avg", "Nodes", "Relays"],
            tablefmt="plain",
        )

        # Split the table into chunks that fit into Discord embed messages
        chunks = [table[i : i + 4096] for i in range(0, len(table), 4096)]

        # Post each chunk as a separate embed message
        for chunk in chunks:
            embed = DiscordEmbed(
                title="Chain Reward Last 24hrs",
                description=f"```\n{chunk}\n```",
                color=0xFF9500,
            )
            self.webhook.add_embed(embed)
            self.webhook.execute()
            self.webhook.remove_embeds()
