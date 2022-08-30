GET_NODES_RUNNER_PERF_QUERY_ID = "get_nodes_runner_perf"
GET_NODES_RUNNER_PERF_QUERY = """query getPerf($domain:String!){
  getNodeRunnerSummary(domain:$domain){
    serviced_last_48_hours
    serviced_last_24_hours
    serviced_last_6_hours
    total_last_48_hours
    total_last_24_hours
    total_last_6_hours
    avg_last_48_hours
    avg_last_24_hours
    avg_last_6_hours
    jailed_now
    total_chains
    total_nodes
    total_balance
  }
}
"""
