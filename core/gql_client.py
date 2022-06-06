import logging
from random import randint
import time
from typing import Dict
from core import utils
from core import constants as cst
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.requests import log as requests_logger

requests_logger.setLevel(logging.ERROR)


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
        logging.info(f'Sending query {query_id}')
        attempt = 0
        while attempt < cst.MAX_RETRIES:
            try:
                logging.info(f'Attemp {attempt} for query {query_id}')
                async with Client(
                    transport=self.transport,
                    fetch_schema_from_transport=True,
                    execute_timeout=20
                ) as session:
                    query = gql(query)
                    result = await session.execute(query, variable_values=params)
                    logging.info(f'Successfully sent query {query_id}')
                    return result
            except Exception as ex:
                logging.warn(
                    f'An exception occured when sending query: {query_id}\nex:{ex}')
                time.sleep(randint(5, 20))
                attempt += 1
                continue
        logging.error(f'Could not fetch data for query: {query_id}')
        return {}
