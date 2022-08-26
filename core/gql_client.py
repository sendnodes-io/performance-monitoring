from gql.transport.websockets import log as websockets_logger
import logging
from random import randint
import time
from typing import Dict
from core import utils
from core import constants as cst
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport, log as aiohttp_logger
from gql.transport.requests import log as requests_logger

# quiet dwn u
aiohttp_logger.setLevel(logging.WARNING)
requests_logger.setLevel(logging.WARNING)
websockets_logger.setLevel(logging.WARNING)


class GqlClient():
    def __init__(self) -> None:
        env_vars = utils.get_env_variables(
            [cst.GRAPHQL_URL_ENV_VAR, cst.GRAPHQL_API_KEY_1_ENV_VAR, cst.GRAPHQL_API_KEY_2_ENV_VAR])
        if not env_vars.get(cst.GRAPHQL_URL_ENV_VAR) or not env_vars.get(cst.GRAPHQL_API_KEY_1_ENV_VAR):
            raise ValueError(
                f'You need to provide a url and an api_key to initialise the client. Got url: {url}')
        logging.debug(f'Initialising client')
        url = env_vars.get(cst.GRAPHQL_URL_ENV_VAR)
        self.transport = AIOHTTPTransport(url=url, headers={
                                          'Authorization': env_vars.get(cst.GRAPHQL_API_KEY_1_ENV_VAR)})
        logging.debug(f'Client successfully created pointing to {url}')

    async def send_query(self, query: str, query_id: str, params: dict = {}) -> Dict:
        """

        """
        logging.debug(f'Sending query {query_id}')
        attempt = 0
        while attempt < cst.MAX_RETRIES:
            try:
                async with Client(
                    transport=self.transport,
                    fetch_schema_from_transport=True,
                    execute_timeout=60
                ) as session:
                    result = await session.execute(gql(query), variable_values=params)
                    logging.info(f'Successfully sent query {query_id}')
                    return result
            except Exception as ex:
                attempt += 1
                logging.warn(
                    f'Attempted {attempt} for query {query_id}, but an exception occured when sending query: {query_id}\n\tex:{ex}')
                time.sleep(randint(15, 30))
                continue
        logging.error(f'Could not fetch data for query: {query_id}')
        return {}
