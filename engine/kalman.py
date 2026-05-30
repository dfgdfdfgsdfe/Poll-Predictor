# =========================================================
# engine/state_space.py
# =========================================================

import numpy as np


# =========================================================
# 상태 벡터 생성
# =========================================================

def create_state_vector(
    supports: dict,
    undecided: float
):
    """
    supports

    {
        "이재명": 44.0,
        "김문수": 39.0,
        "이준석": 7.0
    }

    undecided

    10.0

    반환

    np.array(
        [44.0, 39.0, 7.0, 10.0]
    )
    """

    state = []

    for candidate in supports:

        state.append(
            float(
                supports[candidate]
            )
        )

    state.append(
        float(
            undecided
        )
    )

    return np.array(
        state,
        dtype=float
    )


# =========================================================
# 상태 정규화
# =========================================================

def normalize_state(
    state: np.ndarray
):
    """
    합계를 100으로 정규화
    """

    total = np.sum(
        state
    )

    if total <= 0:

        return state

    return (
        state
        /
        total
    ) * 100.0


# =========================================================
# 후보 수 반환
# =========================================================

def candidate_count(
    state: np.ndarray
):

    return len(state) - 1


# =========================================================
# 무지지자 인덱스
# =========================================================

def undecided_index(
    state: np.ndarray
):

    return len(state) - 1


# =========================================================
# 자동 Q 행렬 생성
# =========================================================

def build_q_matrix(
    n_states: int,
    volatility: float = 0.15
):
    """
    Random Walk 공분산 행렬

    volatility

    0.05 = 매우 안정적

    0.15 = 기본

    0.30 = 매우 변동적
    """

    q = np.zeros(
        (
            n_states,
            n_states
        )
    )

    for i in range(
        n_states
    ):

        q[i, i] = volatility

    for i in range(
        n_states
    ):

        for j in range(
            n_states
        ):

            if i == j:
                continue

            q[i, j] = (
                -volatility
                * 0.25
            )

    return q


# =========================================================
# 하루 상태 전이
# =========================================================

def random_walk_step(
    state: np.ndarray,
    q_matrix: np.ndarray
):
    """
    θ(t)
    =
    θ(t−1)
    +
    η

    η ~ MVN(0,Q)
    """

    noise = np.random.multivariate_normal(
        mean=np.zeros(
            len(state)
        ),
        cov=q_matrix
    )

    next_state = (
        state
        +
        noise
    )

    next_state = np.clip(
        next_state,
        0,
        None
    )

    next_state = normalize_state(
        next_state
    )

    return next_state


# =========================================================
# N일 미래 생성
# =========================================================

def project_to_election_day(
    initial_state: np.ndarray,
    days_remaining: int,
    q_matrix: np.ndarray
):
    """
    반환

    shape

    [days + 1, state_size]
    """

    current = (
        initial_state.copy()
    )

    history = [
        current.copy()
    ]

    for _ in range(
        days_remaining
    ):

        current = random_walk_step(
            current,
            q_matrix
        )

        history.append(
            current.copy()
        )

    return np.array(
        history
    )


# =========================================================
# 최종 상태 반환
# =========================================================

def final_state(
    history: np.ndarray
):

    return history[-1]


# =========================================================
# 상태를 딕셔너리로 변환
# =========================================================

def state_to_dict(
    state: np.ndarray,
    candidate_names: list
):
    """
    state

    [44,39,7,10]

    →

    {
        "이재명":44,
        "김문수":39,
        "이준석":7,
        "UNDECIDED":10
    }
    """

    result = {}

    for idx, candidate in enumerate(
        candidate_names
    ):

        result[candidate] = float(
            state[idx]
        )

    result["UNDECIDED"] = float(
        state[-1]
    )

    return result


# =========================================================
# 딕셔너리를 상태로 변환
# =========================================================

def dict_to_state(
    state_dict: dict,
    candidate_names: list
):
    """
    state_to_dict 역변환
    """

    state = []

    for candidate in candidate_names:

        state.append(
            state_dict[candidate]
        )

    state.append(
        state_dict["UNDECIDED"]
    )

    return np.array(
        state,
        dtype=float
    )
