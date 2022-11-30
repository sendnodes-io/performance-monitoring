<img src="https://comparestakingservices.com/logo-dual.svg" width="760" alt="Compare Staking Services" />

# Compare Staking Services - Pocket Network Performance Monitoring

[Compare Pocket Network Staking Services](https://comparestakingservices.com/)

A comparison of Pocket Network staking services. This list breaks down the services by their staking rewards, staking fees, and staking minimums.

This repo pulls data from poktscan.com to calculate the gross rewards for each staking service provider. The data is then displayed on the website.

> 💁‍♀️ Learn more about Pocket Network at [pokt.network](https://pokt.network).

## 🙋‍♀️ First time here?

Information is incorrect? Can’t find the answer you’re looking for? Reach out to our customer support team below.

- [Twitter](https://t.me/CompareStakingServices)
- [Discord](https://discord.gg/TmfYqaXzGb)

## 👩🏻‍💻 Contributing

SendNodes, Inc. is looking for amazing contributors. Feel free to fork the repo and start shipping code! For the latest news on our roadmap and milestones, please join our Discord server.

## 👷‍♀️ Usage

### Overall flow description

1. We get the list of the top runners from pokt-scan API
2. For each top runners we fetch statistics (avg perf 6 / 24 / 48 hrs)
3. We post to SendNodes Discord channel the statistics
4. We post to twitter the performances

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
python ./main.py
```
