This repo is generating performance reports for the nodes runners based on pokt-scan graphql API.

Sometimes the API doesn't return data for some of the nodes runners - although we attempt to retry on connection failure we won't return data for the node runners which we have failed to fetch from the API.

## Overall flow description

1. We get the list of the top runners from pokt-scan API
2. For each top runners we fetch statistics (avg perf 6 / 24 / 48 hrs)
3. We post to SendNodes Discord channel the statistics
4. We post to twitter the performances

## Usage

### Environment variables

---

In order to operate successfully the bot rely on a few environment variables

- **GRAPHQL_URL**: https://www.poktscan.com/api/graphql,
- **GRAPHQL_API_KEY_1**: KEY FOR GRAPHQL API
- **GRAPHQL_API_KEY_2**: ALT KEY FOR GRAPHQL API
- **AWS_ACCESS_KEY_ID**: AWS IAM KEY
- **AWS_ACCESS_SECRET**: AWS IAM SECRET
- **AWS_S3_BUCKET**:BUCKET NAME
- **AWS_REGION**: AWS S3 REGION
- **DISCORD_HOOK**: HOOK FOR WRITTING TO DISCORD
- **TWITTER_API_KEY**: TWITTER APP ID
- **TWITTER_API_SECRET**: TWITTER APP SECRET
- **TWITTER_ACCESS_TOKEN**: TOKEN FOR WRITTING
- **TWITTER_ACCESS_TOKEN_SECRET**: TOKEN SECRET FOR WRITTING

### Run the program

---

In order to run the program you can specificy command line arguments:

- -d will get the statistics and post the results to Discord
- -t will get the statistics and psot the results to Twitter

```
python ./main.py -d -n 25
```
