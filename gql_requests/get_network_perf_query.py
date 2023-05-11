GET_NETWORK_PERFORMANCE_QUERY_ID = "get_network_performance"
GET_NETWORK_PERFORMANCE_QUERY = """query{
  GetNetworkEarnPerformanceReport {
    servicer {
      thirty_days_max_pokt_avg
      twenty_fours_hs_less_pokt_avg
			thirty_days_pokt_avg

    }
  }
}
"""
