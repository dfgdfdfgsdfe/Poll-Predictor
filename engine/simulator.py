# =========================================================
# engine/simulator.py
# =========================================================

import numpy as np

from engine.state_space import (
    build_forecast_package
)

from engine.sampler import (
    generate_world
)

from data.poll_processor import (
    average_sample_size
)


# =========================================================
# 선거일까지 남은 일수
# =========================================================

def calculate_days_until_election(
    dataframe,
    election_date
):

    latest_poll_date = (
        dataframe["end_date"].max()
    )

    election_date = pd.to_datetime(
        election_date
    )

    delta = (
        election_date - latest_poll_date
    ).days

    return max(delta, 0)


# =========================================================
# 최신 무당층 선호
# =========================================================

def latest_undecided_preferences(
    dataframe,
    candidate_names
):

    latest_row = (
        dataframe.iloc[-1]
    )

    result = {}

    for candidate in candidate_names:

        result[candidate] = float(

            latest_row[
                f"{candidate}_pref"
            ]

        )

    return result


# =========================================================
# World 생성
# =========================================================

def generate_simulation_worlds(
    dataframe,
    candidate_names,
    election_date,
    world_count=100
):

    days_until_election = (
        calculate_days_until_election(
            dataframe,
            election_date
        )
    )

    forecast_package = (

        build_forecast_package(

            dataframe,

            candidate_names,

            days_until_election

        )

    )

    forecast = (
        forecast_package[
            "forecast"
        ]
    )

    preferences = (

        latest_undecided_preferences(

            dataframe,

            candidate_names

        )

    )

    latest_sample_size = (
        average_sample_size(
            dataframe
        )
    )

    supports = {}

    for candidate in candidate_names:

        supports[candidate] = (
            forecast[candidate]
        )

    undecided = (
        forecast["UNDECIDED"]
    )

    worlds = []

    for world_id in range(
        world_count
    ):

        world = generate_world(

            supports,

            undecided,

            preferences,

            latest_sample_size

        )

        world[
            "world_id"
        ] = (
            world_id + 1
        )

        worlds.append(
            world
        )

    return {

        "worlds":
            worlds,

        "forecast":
            forecast,

        "state_space":

            forecast_package[
                "state_space"
            ],

        "summary":

            forecast_package[
                "summary"
            ],

        "days_until_election":
            days_until_election
    }


# =========================================================
# 승률 계산
# =========================================================

def calculate_win_rates(
    worlds
):

    counts = {}

    for world in worlds:

        winner = (
            world["winner"]
        )

        counts[winner] = (

            counts.get(
                winner,
                0
            )

            + 1

        )

    total = len(
        worlds
    )

    result = {}

    for winner, count in counts.items():

        result[winner] = (

            count

            /

            total

        ) * 100

    return result


# =========================================================
# 후보별 예측 테이블
# =========================================================

def build_prediction_table(
    worlds,
    candidate_names
):

    rows = []

    for candidate in candidate_names:

        values = []

        for world in worlds:

            values.append(

                world[
                    "final_result"
                ][candidate]

            )

        rows.append({

            "후보":
                candidate,

            "예상 득표율":

                round(
                    float(
                        np.mean(values)
                    ),
                    2
                ),

            "95% 하한":

                round(
                    float(
                        np.percentile(
                            values,
                            2.5
                        )
                    ),
                    2
                ),

            "95% 상한":

                round(
                    float(
                        np.percentile(
                            values,
                            97.5
                        )
                    ),
                    2
                )

        })

    rows.sort(

        key=lambda x:
        x["예상 득표율"],

        reverse=True

    )

    return rows


# =========================================================
# 전체 실행
# =========================================================

def run_simulation(
    dataframe,
    candidate_names,
    election_date,
    world_count=100
):

    simulation = (

        generate_simulation_worlds(

            dataframe,

            candidate_names,

            election_date,

            world_count

        )

    )

    worlds = (
        simulation[
            "worlds"
        ]
    )

    win_rates = (
        calculate_win_rates(
            worlds
        )
    )

    prediction_table = (

        build_prediction_table(

            worlds,

            candidate_names

        )

    )

    return {

        "worlds":
            worlds,

        "forecast":
            simulation[
                "forecast"
            ],

        "state_space":
            simulation[
                "state_space"
            ],

        "summary":
            simulation[
                "summary"
            ],

        "win_rates":
            win_rates,

        "prediction_table":
            prediction_table,

        "days_until_election":

            simulation[
                "days_until_election"
            ]
    }
