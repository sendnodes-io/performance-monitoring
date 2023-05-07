GET_NODES_RUNNER_PERF_QUERY_ID = "get_nodes_runner_perf"
GET_NODES_RUNNER_PERF_QUERY = """
query getPerf($domain:String!){
  GetSummaryForNodeSelection(input:{service_domain:$domain}){
    relays_last_48hrs
    relays_last_24hrs
    relays_last_6hrs
    servicer_rewards_last_48hrs
    servicer_rewards_last_24hrs
    servicer_rewards_last_6hrs
    producer_rewards_last_48hrs
    producer_rewards_last_24hrs
    producer_rewards_last_6hrs
    total_rewards_last_48hrs
    total_rewards_last_24hrs
    total_rewards_last_6hrs
    avg_relays_last_48hrs
    avg_relays_last_24hrs
    avg_relays_last_6hrs
    avg_servicer_rewards_last_48hrs
    avg_servicer_rewards_last_24hrs
    avg_servicer_rewards_last_6hrs
    avg_base_servicer_rewards_last_48hrs
    avg_base_servicer_rewards_last_24hrs
    avg_base_servicer_rewards_last_6hrs
    avg_total_rewards_last_48hrs
    avg_total_rewards_last_24hrs
    avg_total_rewards_last_6hrs
    avg_producer_rewards_last_48hrs
    avg_producer_rewards_last_24hrs
    avg_producer_rewards_last_6hrs
    producer_times_last_48hrs
    producer_times_last_24hrs
    producer_times_last_6hrs
    total_tokens_staked
    validators_tokens_staked
    validators
    last_height
    total_pending_relays
    total_estimated_pending_rewards
    total_chains
    jailed_now
    total_balance
    total_output_balance
    total_nodes
    nodes_staked
    nodes_unstaked
    nodes_unstaking
  }
}
"""
