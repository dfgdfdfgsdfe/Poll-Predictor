# =========================================================
# Bayesian Sampling Engine
# =========================================================

import numpy as np


# =========================================================
# 후보 + 무지지자 샘플링
# =========================================================

def sample_vote_shares(
    supports,
    undecided,
    sample_size
):
    """
    supports:
    {
        "A":44,
        "B":39,
        "C":7
    }

    undecided:
    10
    """

    labels = list(
        supports.keys()
    )

    observed = [
        supports[c]
        for c in labels
    ]

    observed.append(
        undecided
    )

    alpha = []

    for pct in observed:

        count = (
            pct
            /
            100
        ) * sample_size

        alpha.append(
            count + 1
        )

    draw = np.random.dirichlet(
        alpha
    )

    result = {}

    for i, c in enumerate(
        labels
    ):
        result[c] = (
            draw[i]
            * 100
        )

    result["UNDECIDED"] = (
        draw[-1]
        * 100
    )

    return result


# =========================================================
# 무당층 선호도 샘플링
# =========================================================

def sample_undecided_preferences(
    undecided_pref,
    undecided_pct,
    sample_size
):
    """
    undecided_pref

    {
        "A":60,
        "B":35,
        "C":5
    }
    """

    effective_n = max(
        1,
        round(
            sample_size
            *
            undecided_pct
            /
            100
        )
    )

    labels = list(
        undecided_pref.keys()
    )

    alpha = []

    for c in labels:

        pct = undecided_pref[c]

        count = (
            pct
            /
            100
        ) * effective_n

        alpha.append(
            count + 1
        )

    draw = np.random.dirichlet(
        alpha
    )

    result = {}

    for i, c in enumerate(
        labels
    ):
        result[c] = (
            draw[i]
            * 100
        )

    return result


# =========================================================
# 무지지자 배분
# =========================================================

def allocate_undecided(
    sampled_supports,
    sampled_preferences
):
    """
    sampled_supports

    {
        A:43.8
        B:39.2
        C:7.1
        UNDECIDED:9.9
    }
    """

    undecided = sampled_supports[
        "UNDECIDED"
    ]

    final_result = {}

    for candidate in sampled_preferences:

        final_result[candidate] = (

            sampled_supports[
                candidate
            ]

            +

            undecided

            *

            (
                sampled_preferences[
                    candidate
                ]
                /
                100
            )
        )

    total = sum(
        final_result.values()
    )

    if total <= 0:
        total = 1

    for c in final_result:

        final_result[c] = (

            final_result[c]

            /

            total

        ) * 100

    return final_result


# =========================================================
# 단일 World 생성
# =========================================================

def generate_world(
    supports,
    undecided,
    undecided_pref,
    sample_size
):

    sampled_supports = (
        sample_vote_shares(
            supports,
            undecided,
            sample_size
        )
    )

    sampled_preferences = (
        sample_undecided_preferences(
            undecided_pref,
            sampled_supports[
                "UNDECIDED"
            ],
            sample_size
        )
    )

    final_result = (
        allocate_undecided(
            sampled_supports,
            sampled_preferences
        )
    )

    winner = max(
        final_result,
        key=final_result.get
    )

    return {

        "sampled_supports":
            sampled_supports,

        "sampled_preferences":
            sampled_preferences,

        "final_result":
            final_result,

        "winner":
            winner
    }


# =========================================================
# 다중 World 생성
# =========================================================

def generate_worlds(
    supports,
    undecided,
    undecided_pref,
    sample_size,
    n_worlds=100
):
    worlds = []

    for world_id in range(
        n_worlds
    ):

        world = generate_world(
            supports,
            undecided,
            undecided_pref,
            sample_size
        )

        world["world_id"] = (
            world_id + 1
        )

        worlds.append(
            world
        )

    return worlds


# =========================================================
# 승률 계산
# =========================================================

def calculate_win_rates(
    worlds
):
    counts = {}

    for world in worlds:

        winner = world[
            "winner"
        ]

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

    return {

        candidate:
        (
            wins
            /
            total
        ) * 100

        for candidate,
        wins

        in counts.items()
    }
