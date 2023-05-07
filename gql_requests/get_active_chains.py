GET_ACTIVE_CHAINS_QUERY_ID = "get_active_chains"
GET_ACTIVE_CHAINS = """
query {
  GetActiveChains {
    chain
    time
    height
  }
}
"""
