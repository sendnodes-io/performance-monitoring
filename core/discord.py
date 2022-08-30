from typing import List
from unittest import runner
from core import utils
from core import constants as cst
from discord_webhook import DiscordEmbed, DiscordWebhook
from core.model import NetworkPerformance, RunnerPerformance
import os.path


class DiscordBot():
    def __init__(self) -> None:
        env_var = utils.get_env_variables([cst.DISCORD_WEBHOOK])
        self.discord_hook = env_var.get(cst.DISCORD_WEBHOOK)
        self.webhook = DiscordWebhook(url=env_var.get(
            cst.DISCORD_WEBHOOK), username='Perf Bot')

    def post_network_perf_data(self, network_data: NetworkPerformance):
        description = f'Today Pokt: {network_data.today_pokt}\n30d avg Pokt: {network_data.thirty_day_pokt_avg}'
        embed_net_perf = DiscordEmbed(
            title=f'Network Perf', description=description, color='ffb0e3')
        self.webhook.remove_embeds()
        self.webhook.add_embed(embed_net_perf)
        self.webhook.execute()

    def post_runners_perf_data(self, runners_data: List[RunnerPerformance]):
        for r in runners_data:
            r.runner_domain_sort = 1000 if "sendnodes.org" in r.runner_domain else 0
        # chuncks = [runners_data[x:x+9] for x in range(0, len(runners_data), 9)]
        self.webhook.remove_embeds()
        runners_data.sort(key=lambda r: (r.avg_last_48_hours,
                          r.runner_domain_sort), reverse=True)
        description = '\n'.join(
            [f'{r.runner_domain}:{round(r.avg_last_48_hours)}' for r in runners_data])
        embed_48 = DiscordEmbed(
            title=f"Average 48h", description=description, color='03b2f8')
        self.webhook.add_embed(embed_48)

        # Last 24 hours
        runners_data.sort(key=lambda r: (r.avg_last_24_hours,
                          r.runner_domain_sort), reverse=True)
        description = '\n'.join(
            [f'{r.runner_domain}:{round(r.avg_last_24_hours)}' for r in runners_data])
        embed_24 = DiscordEmbed(
            title=f"Average 24h", description=description, color='66ff66')
        self.webhook.add_embed(embed_24)

        # Last 6 hours
        runners_data.sort(key=lambda r: (r.avg_last_6_hours,
                          r.runner_domain_sort), reverse=True)
        description = '\n'.join(
            [f'{r.runner_domain}:{round(r.avg_last_6_hours)}' for r in runners_data])
        embed_6 = DiscordEmbed(
            title=f"Average 6h", description=description, color='7d7d73')
        self.webhook.add_embed(embed_6)

        # Chains count
        runners_data.sort(key=lambda r: (
            r.total_chains, r.runner_domain_sort), reverse=True)
        description = '\n'.join(
            [f'{r.runner_domain}:{r.total_chains}' for r in runners_data])
        embed_c = DiscordEmbed(
            title=f"# chains", description=description, color='ffff00')
        self.webhook.add_embed(embed_c)

        # Nodes count
        runners_data.sort(key=lambda r: (
            r.total_nodes, r.runner_domain_sort), reverse=True)
        description = '\n'.join(
            [f'{r.runner_domain}:{r.total_nodes}' for r in runners_data])
        embed_n = DiscordEmbed(
            title=f"# nodes", description=description, color='ff66ff')

        self.webhook.add_embed(embed_n)

        # add csv dump if exists
        if os.path.isfile('node_runners.csv'):
            with open("node_runners.csv", "rb") as f:
                self.webhook.add_file(
                    file=f.read(), filename='node_runners.csv')

        self.webhook.execute()

        # logging.info(response)
