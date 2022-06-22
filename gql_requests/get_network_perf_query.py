GET_NETWORK_PERFORMANCE_QUERY_ID = "get_network_performance"
GET_NETWORK_PERFORMANCE_QUERY = """query{
  getPoktEarnPerformance{
    max_pokt,
    max_relays,
    thirty_day_pokt_avg,
    thirty_day_relays_avg,
    today_pokt,
    today_relays
  }
}
"""
