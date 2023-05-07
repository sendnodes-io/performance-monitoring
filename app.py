import decimal
import os
from dotenv import load_dotenv
import csv
from core import model
from core.model import RunnerPerformanceSummary, RunnerPerformanceOrm
from main import get_stats, post_discord_message, servicer_node_summary
from flask import Flask, g, jsonify
from flask_apscheduler import APScheduler
from flask_cors import CORS
from flask_caching import Cache
import logging
from sqlalchemy.orm import Session
import core.db
from datetime import datetime, timedelta, time
from collections import defaultdict
from typing import List

JOBID_GET_RUNNERS_PERF_DATA = "do_post_runners_perf_data"

JOBID_RUNNER_PERF_7D = "do_calc_runners_perf_7d_data"

CACHE_RUNNER_PERF_7D = "runners_perf_7d"

load_dotenv()

# Initialise logger
logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")


class Config:
    SCHEDULER_API_ENABLED = True
    DEBUG = os.environ.get("FLASK_ENV", "development") == "development"
    CACHE_TYPE = "SimpleCache"


# create app
app = Flask(__name__)
CORS(app)
app.config.from_object(Config())

# initialize cache
cache = Cache(app)

# initialize scheduler
scheduler = APScheduler()
scheduler.init_app(app)

# global variables for holding data in memory
netperf_data = None
runners_perf_data = None
runners_perf_data_7d = None


def calc_runners_perf_data() -> tuple:
    return get_stats(int(os.environ.get("APP_TOP_NODE_RUNNERS", 25)))


@scheduler.task("cron", id=JOBID_GET_RUNNERS_PERF_DATA, hour="*")
def post_runners_perf_data():
    with scheduler.app.app_context():
        global netperf_data
        global runners_perf_data
        netperf_data, runners_perf_data, chain_rewards = calc_runners_perf_data()

        # generate csv file
        keys = list(
            {
                k: v for k, v in runners_perf_data[0].dict().items() if v is not None
            }.keys()
        )
        with open("node_runners.csv", "w", newline="") as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(
                [
                    {k: v for k, v in rp.dict().items() if v is not None}
                    for rp in runners_perf_data
                ]
            )

        print([netperf_data])
        print(runners_perf_data)

        # post to discord
        post_discord_message(netperf_data, runners_perf_data, chain_rewards)

        # signal to the api that we have new data
        enqueue_do_post_runners_perf_7d_data()

        return runners_perf_data


@app.route("/")
def hello():
    return "<h1>Hello, World!</h1>"


def enqueue_do_post_runners_perf_data():
    for job in scheduler.get_jobs():
        if job.id == JOBID_GET_RUNNERS_PERF_DATA:
            job.modify(next_run_time=datetime.now())


@app.route("/v1/runners-perf")
@cache.cached(timeout=10)
def runners_perf():
    global netperf_data
    global runners_perf_data

    if runners_perf_data is None:
        enqueue_do_post_runners_perf_data()
        return jsonify({"error": "No data available"}), 404
    else:
        # noinspection PyTypeChecker
        return jsonify(
            [
                {k: v for k, v in rp.dict().items() if v is not None}
                for rp in runners_perf_data
            ]
        )


def get_closest_to_midnight(
    rows: List[RunnerPerformanceOrm],
) -> List[RunnerPerformanceOrm]:
    # group rows by date
    rows_by_date = defaultdict(list)
    for row in rows:
        rows_by_date[row.created_at.date()].append(row)

    closest_rows = []
    for date, rows in rows_by_date.items():
        # find the row closest to midnight for this date
        closest_row = min(
            rows,
            key=lambda row: abs(
                datetime.combine(date, row.created_at.time())
                - datetime.combine(date, time(0))
            ),
        )
        closest_rows.append(closest_row)

    return closest_rows


# Calculate the servicer rewards if the servicer was staked for 15k POKT for the dates
def avg_serviced_summary(rows: List[RunnerPerformanceOrm]) -> RunnerPerformanceSummary:
    total_serviced = decimal.Decimal(0.0)
    total_num_of_15k_pokt_nodes = decimal.Decimal(0.0)
    total_dates = {}

    if len(rows) == 0:
        return RunnerPerformanceSummary(
            runner_domain="",
            rows=[],
            avg_serviced=decimal.Decimal(0.0),
            avg_num_of_15k_pokt_nodes=decimal.Decimal(0.0),
        )

    rows_as_dict = []
    for row in rows:
        if row.created_at.date() not in total_dates:
            total_dates[row.created_at.date()] = True
            total_serviced += row.serviced_last_24_hours
            num_of_15k_pokt_nodes = decimal.Decimal(
                servicer_node_summary(
                    row.validators, row.total_validator_tokens_staked, row.tokens
                )
            )
            total_num_of_15k_pokt_nodes += num_of_15k_pokt_nodes
            _dict = row.__dict__
            _dict.pop("_sa_instance_state", None)
            _dict["num_of_15k_pokt_nodes"] = num_of_15k_pokt_nodes
            rows_as_dict.append(_dict)

    return RunnerPerformanceSummary(
        runner_domain=rows[0].runner_domain,
        rows=rows_as_dict,
        avg_serviced=total_serviced / (total_num_of_15k_pokt_nodes / len(total_dates)),
        avg_num_of_15k_pokt_nodes=total_num_of_15k_pokt_nodes / len(total_dates),
    )


@scheduler.task(
    "cron", id=("%s" % JOBID_RUNNER_PERF_7D), hour="0", minute="0", second="0"
)
def do_calculate_runners_perf_7d():
    with scheduler.app.app_context():
        calculate_runners_perf_7d(True)


def calculate_runners_perf_7d(force_refresh: bool = False) -> dict:
    global runners_perf_data_7d
    end_date = datetime.now().date() - timedelta(days=1)
    start_date = end_date - timedelta(days=7)

    if force_refresh is False and runners_perf_data_7d is not None:
        return runners_perf_data_7d

    with Session(core.db.ENGINE) as session:
        rows = (
            session.query(RunnerPerformanceOrm)
            .filter(
                RunnerPerformanceOrm.created_at > start_date,
                RunnerPerformanceOrm.created_at < end_date,
            )
            .all()
        )

        # group rows by runner_domain
        rows_by_runner = defaultdict(list)
        for row in rows:
            rows_by_runner[row.runner_domain].append(row)

        # find the closest row for each date for each runner_domain
        closest_rows_by_runner = {}
        for runner_domain, rows in rows_by_runner.items():
            closest_rows_by_runner[runner_domain] = get_closest_to_midnight(rows)

        # summarize the closest rows for each runner_domain
        summary_rows_by_runner = {}
        for runner_domain, rows in closest_rows_by_runner.items():
            summary_rows_by_runner[runner_domain] = avg_serviced_summary(rows)

        result = {
            "summary_rows_by_runner": summary_rows_by_runner,
            "end_date": end_date,
            "start_date": start_date,
        }

        runners_perf_data_7d = result

        return runners_perf_data_7d


def enqueue_do_post_runners_perf_7d_data():
    for job in scheduler.get_jobs():
        if job.id == JOBID_RUNNER_PERF_7D:
            job.modify(next_run_time=datetime.now())


@app.route("/v2/runners-perf")
@cache.cached(timeout=10)
def runners_perf_v2():
    data = calculate_runners_perf_7d()

    # create a list of dictionaries representing the merged rows
    result = []
    for runner_domain, perf7d in data["summary_rows_by_runner"].items():
        result.append(
            {
                "runner_domain": perf7d.runner_domain,
                "avg_serviced_per_15k": perf7d.avg_serviced,
                "rows": perf7d.rows,
                "end_date": data["end_date"],
                "start_date": data["start_date"],
            }
        )

    # return the result as a JSON object
    return jsonify(result)


logging.info("Starting app")
scheduler.start()

if __name__ == "__main__":
    app.run()
