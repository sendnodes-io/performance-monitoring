GET_CHAINS_REWARDS_QUERY_ID = 'get_chains_rewards'
GET_CHAINS_REWARDS_QUERY = """
query getChainsRewards($from: String!, $to: String!, $timeSeriesAggregation: TimeSeriesAggregation, $interval: BigInt) {
  getChainsRewards(
    from: $from
    to: $to
    timeSeriesAggregation: $timeSeriesAggregation
    interval: $interval
  ) {
    first
    first_time
    last
    last_time
    total_relays
    total_pokt
    total_by_chain {
      chain
      total_relays
      total_pokt
      __typename
    }
    units {
      first
      last
      point_id
      point
      chains {
        chain
        total_relays
        total_pokt
        validators_avg
        earn_avg
        __typename
      }
      __typename
    }
    __typename
  }
}
"""
