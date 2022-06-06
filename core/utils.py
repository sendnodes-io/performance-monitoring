import os
import logging
from typing import Dict, List


def get_env_variables(env_var_names: List[str]) -> Dict:
    """
        Helper to retrieve environment variables values
    """
    logging.debug(f'Getting {env_var_names} from registry')
    if not env_var_names:
        raise ValueError(
            f'Your need to specify a non empty, got:  {env_var_names}')
    result = {}
    for ev in env_var_names:
        try:
            if not ev:
                raise ValueError(
                    f'An error occcurred when getting env vars, got key: {ev}')
            result[ev] = os.environ.get(ev)
        except Exception as ex:
            logging.error(
                f'An error occcurred when getting env vars, got key: {ex}')
    return result
