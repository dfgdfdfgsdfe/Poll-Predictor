# =========================================================
# engine/simulator.py
# =========================================================

import numpy as np
import pandas as pd

from engine.kalman import (
    build_filtered_state
)

from engine.sampler import (
    sample_vote_shares,
    sample_undecided_preferences,
    allocate_undecided
)

from engine.state_space import (
    create_state_vector,
    build_q_matrix,
    project_to_election_day,
    final_state
)


# =========================================================
# 선거일까지 남은 일수
# =========================================================

def calculate_days_remaining(
    latest_poll_date,
    election_date
):

    latest_poll_date = pd.to_datetime(
        latest_poll_date
    )

    election_date = pd.to_datetime(
        election_date
    )

    days = (
        election_date
        -
        latest_poll_date
    ).days

    return max(
        days,
        0
    )


# =========================================================
# 단일 World 생성
# =========================================================

def simulate_world(
    filtered_state,
    undecided_preferences,
    sample_size,
    candidate_names,
    days_remaining,
    volatility=0.15
):

    supports = {}

    for c in candidate_names:

        supports[c] = (
            filtered_state[c]
        )

    undecided = (
        filtered_state[
            "UNDECIDED"
        ]
    )

    sampled_supports = (
        sample_vote_shares(
            supports,
            undecided,
            sample_size
        )
    )

    sampled_preferences = (
        sample_undecided_preferences(
            undecided_preferences,
            sampled_supports[
                "UNDECIDED"
            ],
            sample_size
        )
    )

    initial_result = (
        allocate_undecided(
            sampled_supports,
            sampled_preferences
        )
    )

    state = create_state_vector(
        initial_result,
        0.0
    )

    q_matrix = build_q_matrix(
        len(state),
        volatility
    )

    history = (
        project_to_election_day(
            state,
            days_remaining,
            q_matrix
        )
    )

    election_state = (
        final_state(
            history
        )
    )

    final_result = {}

    for idx, c in enumerate(
        candidate_names
    ):

        final_result[c] = float(
            election_state[idx]
        )

    winner = max(
        final_result,
        key=final_result.get
    )

    return {

        "winner":
            winner,

        "final_result":
            final_result,

        "history":
            history
    }


# =========================================================
# 승률 계산
# =========================================================

def calculate_win_rates(
    worlds,
    candidate_names
):

    wins = {

        c: 0

        for c in candidate_names
    }

    for world in worlds:

        wins[
            world["winner"]
        ] += 1

    total = len(
        worlds
    )

    result = {}

    for c in candidate_names:

        result[c] = (

            wins[c]

            /

            total

        ) * 100

    return result


# =========================================================
# 예측 구간 계산
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

        values = np.array(
            values
        )

        rows.append({

            "candidate":
                candidate,

            "mean":
                float(
                    np.mean(
                        values
                    )
                ),

            "lower":
                float(
                    np.percentile(
                        values,
                        2.5
                    )
                ),

            "upper":
                float(
                    np.percentile(
                        values,
                        97.5
                    )
                )
        })

    return pd.DataFrame(
        rows
    )


# =========================================================
# 메인 시뮬레이션
# =========================================================

def run_simulation(
    dataframe,
    candidate_names,
    undecided_preferences,
    election_date,
    world_count=100
):

    filtered_state = (
        build_filtered_state(
            dataframe,
            candidate_names
        )
    )

    latest_poll_date = (
        dataframe[
            "end_date"
        ].max()
    )

    sample_size = int(

        dataframe[
            "sample_size"
        ].mean()

    )

    days_remaining = (
        calculate_days_remaining(
            latest_poll_date,
            election_date
        )
    )

    worlds = []

    for _ in range(
        world_count
    ):

        world = simulate_world(

            filtered_state,

            undecided_preferences,

            sample_size,

            candidate_names,

            days_remaining

        )

        worlds.append(
            world
        )

    prediction_table = (
        build_prediction_table(
            worlds,
            candidate_names
        )
    )

    win_rates = (
        calculate_win_rates(
            worlds,
            candidate_names
        )
    )

    return {

        "worlds":
            worlds,

        "prediction_table":
            prediction_table,

        "win_rates":
            win_rates,

        "filtered_state":
            filtered_state
    }
