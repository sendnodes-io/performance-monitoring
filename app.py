from datetime import datetime
import os
from dotenv import load_dotenv
import csv
from core import model
from core.model import RunnerPerformance
from main import get_stats, post_discord_message
from flask import Flask, g, jsonify
from flask_apscheduler import APScheduler
from flask_cors import CORS
import logging
from sqlalchemy import text
from sqlalchemy.orm import Session
import core.db

load_dotenv()

# Initialise logger
logging.basicConfig(level=logging.INFO,
                    format='%(name)s - %(levelname)s - %(message)s')


class Config:
    SCHEDULER_API_ENABLED = False


# create app
app = Flask(__name__)
CORS(app)
app.config.from_object(Config())

# initialize scheduler
scheduler = APScheduler()
scheduler.init_app(app)

# global variables for holding data in memory
netperf_data = None
runners_perf_data = None


def get_runners_perf_data():
    global netperf_data
    global runners_perf_data
    netperf_data, runners_perf_data = calc_runners_perf_data()
    return runners_perf_data


def calc_runners_perf_data():
    return get_stats(
        int(os.environ.get('APP_TOP_NODE_RUNNERS', 25))
    )


@scheduler.task('cron', id='do_post_runners_perf_data', hour='*')
def post_runners_perf_data():
    global netperf_data
    global runners_perf_data
    netperf_data, runners_perf_data = calc_runners_perf_data()

    # save runners_perf_data to database
    with Session(core.db.ENGINE) as session:
        for runner in runners_perf_data:
            session.merge(model.RunnerPerformanceOrm(
                runner_domain=runner.runner_domain,
                relays_last_48_hours=runner.relays_last_48_hours,
                relays_last_24_hours=runner.relays_last_24_hours,
                relays_last_6_hours=runner.relays_last_6_hours,
                serviced_last_48_hours=runner.serviced_last_48_hours,
                serviced_last_24_hours=runner.serviced_last_24_hours,
                serviced_last_6_hours=runner.serviced_last_6_hours,
                producer_rewards_last_48_hours=runner.producer_rewards_last_48_hours,
                producer_rewards_last_24_hours=runner.producer_rewards_last_24_hours,
                producer_rewards_last_6_hours=runner.producer_rewards_last_6_hours,
                total_last_48_hours=runner.total_last_48_hours,
                total_last_24_hours=runner.total_last_24_hours,
                total_last_6_hours=runner.total_last_6_hours,
                avg_relays_last_48_hours=runner.avg_relays_last_48_hours,
                avg_relays_last_24_hours=runner.avg_relays_last_24_hours,
                avg_relays_last_6_hours=runner.avg_relays_last_6_hours,
                avg_last_48_hours=runner.avg_last_48_hours,
                avg_last_24_hours=runner.avg_last_24_hours,
                avg_last_6_hours=runner.avg_last_6_hours,
                avg_base_last_48_hours=runner.avg_base_last_48_hours,
                avg_base_last_24_hours=runner.avg_base_last_24_hours,
                avg_base_last_6_hours=runner.avg_base_last_6_hours,
                avg_total_last_48_hours=runner.avg_total_last_48_hours,
                avg_total_last_24_hours=runner.avg_total_last_24_hours,
                avg_total_last_6_hours=runner.avg_total_last_6_hours,
                avg_producer_last_48_hours=runner.avg_producer_last_48_hours,
                avg_producer_last_24_hours=runner.avg_producer_last_24_hours,
                avg_producer_last_6_hours=runner.avg_producer_last_6_hours,
                producer_times_last_48_hours=runner.producer_times_last_48_hours,
                producer_times_last_24_hours=runner.producer_times_last_24_hours,
                producer_times_last_6_hours=runner.producer_times_last_6_hours,
                total_tokens_staked=runner.total_tokens_staked,
                total_validator_tokens_staked=runner.total_validator_tokens_staked,
                validators=runner.validators,
                last_height=runner.last_height,
                total_pending_relays=runner.total_pending_relays,
                total_estimated_pending_rewards=runner.total_estimated_pending_rewards,
                total_chains=runner.total_chains,
                jailed_now=runner.jailed_now,
                total_balance=runner.total_balance,
                total_output_balance=runner.total_output_balance,
                total_nodes=runner.total_nodes,
                nodes_staked=runner.nodes_staked,
                nodes_unstaked=runner.nodes_unstaked,
                nodes_unstaking=runner.nodes_unstaking,
                tokens=runner.tokens,
                created_at=datetime.now()
            ))
        session.commit()

    # post to discord

    # generate csv file
    keys = list(
        {k: v for k, v in runners_perf_data[0].dict().items() if v is not None}.keys())
    with open('node_runners.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(
            [{k: v for k, v in rp.dict().items() if v is not None}
             for rp in runners_perf_data]
        )

    print([netperf_data])
    print(runners_perf_data)

    post_discord_message(netperf_data, runners_perf_data)

    return runners_perf_data


@app.route('/')
def hello():
    return '<h1>Hello, World!</h1>'


@app.route('/v1/runners-perf')
def runners_perf():
    global netperf_data
    global runners_perf_data

    if runners_perf_data is None:

        for job in scheduler.get_jobs():
            job.modify(next_run_time=datetime.now())

        return jsonify({'error': 'No data available'}), 404
    else:
        # noinspection PyTypeChecker
        return jsonify([{k: v for k, v in rp.dict().items() if v is not None} for rp in runners_perf_data])


@app.route('/v2/runners-perf')
def runners_perf_v2():
    with core.db.ENGINE.connect() as conn:
        data = conn.execute(text("""
select runner_domain,
       avg(avg_last_48_hours) as "7d_avg_last_48_hours",
       avg(avg_last_24_hours) as "7d_avg_last_24_hours",
       avg(avg_last_6_hours)  as "7d_avg_last_6_hours",
       avg(total_chains)      as "7d_avg_total_chains",
       avg(total_nodes)       as "7d_avg_total_nodes",
       avg(tokens)            as "7d_avg_tokens"
from runner_performance
where created_at > now() - interval '7 day'
group by runner_domain
""")).all()
        return jsonify([dict(row) for row in data])


logging.info('Starting app')
scheduler.start()

if __name__ == "__main__":
    app.run()
