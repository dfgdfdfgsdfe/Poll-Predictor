# =========================================================
# engine/simulator.py
# =========================================================

import numpy as np

from engine.state_space import (
    estimate_state_space,
    forecast_to_election
)

from engine.sampler import (
    generate_world
)


# =========================================================
# 선거일까지 남은 일수
# =========================================================

def days_until_election(
    dataframe,
    election_date
):

    latest_poll = (
        dataframe["end_date"]
        .max()
    )

    delta = (

        election_date

        -

        latest_poll

    ).days

    return max(
        delta,
        0
    )


# =========================================================
# 최신 무당층 선호
# =========================================================

def latest_preferences(
    dataframe,
    candidate_names
):

    latest = dataframe.iloc[-1]

    result = {}

    for candidate in candidate_names:

        result[candidate] = float(

            latest[
                f"{candidate}_pref"
            ]

        )

    return result


# =========================================================
# Forecast 생성
# =========================================================

def build_forecast(
    dataframe,
    candidate_names,
    election_date
):

    state_space = (

        estimate_state_space(

            dataframe,

            candidate_names

        )

    )

    days = days_until_election(

        dataframe,

        election_date

    )

    forecast = (

        forecast_to_election(

            state_space,

            days

        )

    )

    return {

        "state_space":
            state_space,

        "forecast":
            forecast,

        "days":
            days
    }


# =========================================================
# World 생성
# =========================================================

def simulate_worlds(
    dataframe,
    candidate_names,
    election_date,
    n_worlds=100
):

    forecast_data = (

        build_forecast(

            dataframe,

            candidate_names,

            election_date

        )

    )

    forecast = (
        forecast_data[
            "forecast"
        ]
    )

    preferences = (

        latest_preferences(

            dataframe,

            candidate_names

        )

    )

    latest_sample_size = int(

        dataframe[
            "sample_size"
        ].iloc[-1]

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
        n_worlds
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

            forecast_data[
                "state_space"
            ],

        "days_until_election":

            forecast_data[
                "days"
            ]
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

    rates = {}

    for candidate, wins in counts.items():

        rates[candidate] = (

            wins

            /

            total

        ) * 100

    return rates


# =========================================================
# 결과 테이블
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

                float(
                    np.mean(values)
                ),

            "95% 하한":

                float(
                    np.percentile(
                        values,
                        2.5
                    )
                ),

            "95% 상한":

                float(
                    np.percentile(
                        values,
                        97.5
                    )
                )
        })

    rows.sort(

        key=lambda x:
        x["예상 득표율"],

        reverse=True
    )

    return rows
