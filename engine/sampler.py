# =========================================================
# engine/sampler.py
# =========================================================

import numpy as np


# =========================================================
# 후보 + 무당층 동시 샘플링
# Dirichlet 기반
# =========================================================

def sample_supports(
    supports: dict,
    undecided: float,
    sample_size: int
):
    """
    입력:

    supports
    {
        "A":44,
        "B":39,
        "C":7
    }

    undecided = 10

    sample_size = 1000

    출력:

    {
        "A":43.8,
        "B":40.1,
        "C":6.7,
        "UNDECIDED":9.4
    }
    """

    if sample_size <= 0:
        raise ValueError(
            "sample_size must be > 0"
        )

    labels = list(
        supports.keys()
    )

    values = [
        supports[c]
        for c in labels
    ]

    values.append(
        undecided
    )

    alpha = []

    for v in values:

        count = (
            v / 100.0
        ) * sample_size

        alpha.append(
            count + 1.0
        )

    draw = np.random.dirichlet(
        alpha
    )

    result = {}

    for i, c in enumerate(
        labels
    ):
        result[c] = (
            float(draw[i])
            * 100
        )

    result["UNDECIDED"] = (
        float(draw[-1])
        * 100
    )

    return result


# =========================================================
# 무당층 선호도 샘플링
# Beta 기반
# =========================================================

def sample_preference(
    undecided_pref: dict,
    undecided_percent: float,
    sample_size: int
):
    """
    입력:

    undecided_pref
    {
        "A":60,
        "B":35,
        "C":5
    }

    undecided_percent = 10

    sample_size = 1000

    출력:

    {
        "A":58.7,
        "B":36.2,
        "C":5.1
    }
    """

    undecided_n = max(
        int(
            sample_size
            *
            undecided_percent
            /
            100
        ),
        1
    )

    sampled = {}

    for candidate, pref in undecided_pref.items():

        success = (
            pref
            /
            100
        ) * undecided_n

        alpha = success + 1

        beta = (
            undecided_n
            -
            success
            +
            1
        )

        sampled[candidate] = (
            np.random.beta(
                alpha,
                beta
            )
            * 100
        )

    total = sum(
        sampled.values()
    )

    if total <= 0:
        total = 1

    for c in sampled:

        sampled[c] = (
            sampled[c]
            /
            total
        ) * 100

    return sampled


# =========================================================
# 최종 득표율 계산
# =========================================================

def allocate_undecided(
    sampled_supports: dict,
    sampled_preferences: dict
):
    """
    입력

    supports

    {
        "A":44,
        "B":39,
        "C":7,
        "UNDECIDED":10
    }

    preferences

    {
        "A":60,
        "B":35,
        "C":5
    }

    출력

    {
        "A":50,
        "B":42.5,
        "C":7.5
    }
    """

    undecided = sampled_supports[
        "UNDECIDED"
    ]

    result = {}

    for c in sampled_preferences:

        result[c] = (

            sampled_supports[c]

            +

            undecided

            *

            (
                sampled_preferences[c]
                /
                100
            )
        )

    total = sum(
        result.values()
    )

    if total <= 0:
        total = 1

    for c in result:

        result[c] = (
            result[c]
            /
            total
        ) * 100

    return result


# =========================================================
# 단일 World 생성
# =========================================================

def generate_world(
    supports: dict,
    undecided: float,
    undecided_pref: dict,
    sample_size: int
):
    """
    하나의 가능세계 생성
    """

    sampled_supports = (
        sample_supports(
            supports,
            undecided,
            sample_size
        )
    )

    sampled_preferences = (
        sample_preference(
            undecided_pref,
            sampled_supports[
                "UNDECIDED"
            ],
            sample_size
        )
    )

    final_supports = (
        allocate_undecided(
            sampled_supports,
            sampled_preferences
        )
    )

    winner = max(
        final_supports,
        key=final_supports.get
    )

    return {

        "sampled_supports":
            sampled_supports,

        "sampled_preferences":
            sampled_preferences,

        "final_supports":
            final_supports,

        "winner":
            winner
    }


# =========================================================
# 여러 World 생성
# =========================================================

def generate_worlds(
    supports: dict,
    undecided: float,
    undecided_pref: dict,
    sample_size: int,
    n_worlds: int
):
    """
    n개의 가능세계 생성
    """

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
    """
    worlds 목록에서
    후보별 승률 계산
    """

    if len(worlds) == 0:
        return {}

    win_counts = {}

    for world in worlds:

        winner = world["winner"]

        if winner not in win_counts:

            win_counts[
                winner
            ] = 0

        win_counts[
            winner
        ] += 1

    total = len(
        worlds
    )

    results = {}

    for candidate in win_counts:

        results[candidate] = (

            win_counts[
                candidate
            ]

            /

            total

        ) * 100

    return results
