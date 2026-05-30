# =========================================================
# engine/sampler.py
# =========================================================

import numpy as np


# =========================================================
# Dirichlet Alpha 생성
# =========================================================

def build_alpha_from_percentages(
    percentages,
    sample_size
):
    """
    percentages

    [44,39,7,10]

    sample_size

    1000

    →
    alpha
    """

    alpha = []

    for pct in percentages:

        count = (

            pct
            /
            100.0

        ) * sample_size

        alpha.append(
            count + 1
        )

    return alpha


# =========================================================
# 후보 + 무지지자 샘플링
# =========================================================

def sample_vote_shares(
    supports,
    undecided,
    sample_size
):
    """
    반환

    {
        A:44.2,
        B:38.8,
        C:7.3,
        UNDECIDED:9.7
    }
    """

    labels = list(
        supports.keys()
    )

    percentages = []

    for candidate in labels:

        percentages.append(
            supports[candidate]
        )

    percentages.append(
        undecided
    )

    alpha = (
        build_alpha_from_percentages(
            percentages,
            sample_size
        )
    )

    draw = np.random.dirichlet(
        alpha
    )

    result = {}

    for idx, candidate in enumerate(
        labels
    ):

        result[candidate] = (
            draw[idx]
            * 100
        )

    result["UNDECIDED"] = (
        draw[-1]
        * 100
    )

    return result


# =========================================================
# 무당층 선호 샘플링
# =========================================================

def sample_undecided_preferences(
    undecided_preferences,
    undecided_share,
    sample_size
):
    """
    무지지자 규모에 따라
    유효 표본수 계산

    예

    10%

    ×

    1000

    =

    100명
    """

    effective_n = max(

        1,

        round(

            sample_size

            *

            undecided_share

            /

            100

        )
    )

    labels = list(
        undecided_preferences.keys()
    )

    percentages = []

    for candidate in labels:

        percentages.append(

            undecided_preferences[
                candidate
            ]

        )

    alpha = (
        build_alpha_from_percentages(
            percentages,
            effective_n
        )
    )

    draw = np.random.dirichlet(
        alpha
    )

    result = {}

    for idx, candidate in enumerate(
        labels
    ):

        result[candidate] = (
            draw[idx]
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
    최종 득표율 계산
    """

    undecided = (

        sampled_supports[
            "UNDECIDED"
        ]

    )

    result = {}

    for candidate in sampled_preferences:

        result[candidate] = (

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
        result.values()
    )

    if total <= 0:

        total = 1

    for candidate in result:

        result[candidate] = (

            result[candidate]

            /

            total

        ) * 100

    return result


# =========================================================
# 단일 World 생성
# =========================================================

def generate_world(
    supports,
    undecided,
    undecided_preferences,
    sample_size
):
    """
    가능세계 1개
    """

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
    undecided_preferences,
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

            undecided_preferences,

            sample_size

        )

        world[
            "world_id"
        ] = (
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

    results = {}

    for candidate, wins in counts.items():

        results[candidate] = (

            wins

            /

            total

        ) * 100

    return results
