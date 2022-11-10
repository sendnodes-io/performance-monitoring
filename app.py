from datetime import datetime
import os
from dotenv import load_dotenv
import csv
from main import get_stats, post_discord_message
from flask import Flask, g, jsonify
from flask_apscheduler import APScheduler
from flask_cors import CORS
import logging

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
        return jsonify([{k: v for k, v in rp.dict().items() if v is not None} for rp in runners_perf_data])


scheduler.start()

if __name__ == "__main__":
    app.run()
