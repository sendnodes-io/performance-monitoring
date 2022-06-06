GET_LARGEST_NODES_RUNNERS_QUERY_ID = 'get_largest_nodes_runners'
GET_LARGEST_NODES_RUNNERS_QUERY = """query{
  largestNodeRunners{
    items{
      service_domain
      validators
      power
    }
    total_power
  }
}
"""
