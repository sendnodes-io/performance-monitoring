import logging
from typing import List
from core import utils
from core import constants as cst
from discord_webhook import DiscordEmbed, DiscordWebhook
from core.model import RunnerPerformance


class DiscordBot():
    def __init__(self) -> None:
        env_var = utils.get_env_variables([cst.DISCORD_WEBHOOK])
        self.discord_hook = env_var.get(cst.DISCORD_WEBHOOK)
        self.webhook = DiscordWebhook(url=env_var.get(
            cst.DISCORD_WEBHOOK), username='Perf Bot')

    def post_runners_perf_data(self, runners_data: List[RunnerPerformance]):
        chuncks = [runners_data[x:x+9] for x in range(0, len(runners_data), 9)]

        for i, c in enumerate(chuncks):
            embed_48 = DiscordEmbed(
                title=f"Average 48h ({i}/{len(chuncks)})", description=f'Avg last 48h', color='03b2f8')
            for r in c:
                embed_48.add_embed_field(name=r.runner_domain,
                                         value=round(r.avg_last_48_hours))
            self.webhook.add_embed(embed_48)
        for i, c in enumerate(chuncks):
            embed_24 = DiscordEmbed(
                title=f"Average 24h ({i}/{len(chuncks)})", description=f'Avg last 24h', color='66ff66')
            for r in c:
                embed_24.add_embed_field(name=r.runner_domain,
                                         value=round(r.avg_last_24_hours))
            self.webhook.add_embed(embed_24)
        for i, c in enumerate(chuncks):
            embed_c = DiscordEmbed(
                title=f"# chains ({i}/{len(chuncks)})", description=f'Total chains', color='ffff00')
            for r in c:
                embed_c.add_embed_field(name=r.runner_domain,
                                        value=round(r.total_chains))
            self.webhook.add_embed(embed_c)
        for i, c in enumerate(chuncks):
            embed_n = DiscordEmbed(
                title=f"# nodes ({i}/{len(chuncks)})", description=f'Total nodes', color='ff66ff')
            for r in c:
                embed_n.add_embed_field(name=r.runner_domain,
                                        value=round(r.total_nodes))
            self.webhook.add_embed(embed_n)

        response = self.webhook.execute()
        logging.info(response)
