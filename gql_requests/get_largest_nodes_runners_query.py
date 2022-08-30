GET_LARGEST_NODES_RUNNERS_QUERY_ID = 'get_largest_nodes_runners'
GET_LARGEST_NODES_RUNNERS_QUERY = """query{
  largestNodeRunners{
    items{
      service_domain
      tokens
      # power
      # validators_power
      # validators
      # validators_tokens
      # staked
      # jailed
    }
    total_tokens
  }
}
"""
