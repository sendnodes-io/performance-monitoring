GET_CHAINS_REWARDS_BETWEEN_DATES_QUERY_ID = "get_chains_rewards_between_dates"
GET_CHAINS_REWARDS_BETWEEN_DATES = """
query($start:String!, $end:String!, $format: String!) {
  GetChainsRewardsBetweenDates(
    input: {
      # "YYYY-MM-DDTHH:mm:ss.SSSZ"
      start_date: $start
      end_date: $end,
      date_format: $format
    }
  ) {
    chain
    total_relays
    total_pokt
    staked_nodes_avg
    pokt_avg
    relays_avg
  }
}
"""
