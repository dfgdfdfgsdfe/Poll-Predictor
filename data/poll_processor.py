# =========================================================
# data/poll_processor.py
# =========================================================

import pandas as pd

from data.models import (
    ElectionProject
)


# =========================================================
# Poll → Row 변환
# =========================================================

def poll_to_row(
    poll,
    candidate_names
):
    """
    Poll 객체
    ↓
    DataFrame Row
    """

    row = {

        "pollster":
            poll.pollster,

        "start_date":
            pd.to_datetime(
                poll.start_date
            ),

        "end_date":
            pd.to_datetime(
                poll.end_date
            ),

        "sample_size":
            int(
                poll.sample_size
            ),

        "undecided":
            float(
                poll.undecided
            )
    }

    # 후보 지지율

    for candidate in candidate_names:

        row[candidate] = float(

            poll.supports.get(
                candidate,
                0.0
            )

        )

    # 무당층 선호

    for candidate in candidate_names:

        row[
            f"{candidate}_pref"
        ] = float(

            poll.undecided_preferences.get(
                candidate,
                0.0
            )

        )

    return row


# =========================================================
# Project → DataFrame
# =========================================================

def project_to_dataframe(
    project: ElectionProject
):

    rows = []

    for poll in project.polls:

        rows.append(

            poll_to_row(
                poll,
                project.candidate_names
            )

        )

    if len(rows) == 0:

        return pd.DataFrame()

    df = pd.DataFrame(
        rows
    )

    df = df.sort_values(
        "end_date"
    )

    df = df.reset_index(
        drop=True
    )

    return df


# =========================================================
# 날짜 범위
# =========================================================

def get_poll_date_range(
    dataframe
):

    if len(dataframe) == 0:

        return None, None

    return (

        dataframe[
            "start_date"
        ].min(),

        dataframe[
            "end_date"
        ].max()

    )


# =========================================================
# 평균 표본수
# =========================================================

def average_sample_size(
    dataframe
):

    if len(dataframe) == 0:

        return 0

    return int(

        dataframe[
            "sample_size"
        ].mean()

    )


# =========================================================
# 최신 조사일
# =========================================================

def latest_poll_date(
    dataframe
):

    if len(dataframe) == 0:

        return None

    return dataframe[
        "end_date"
    ].max()


# =========================================================
# 후보별 평균 지지율
# =========================================================

def candidate_means(
    dataframe,
    candidate_names
):

    result = {}

    for candidate in candidate_names:

        result[candidate] = float(

            dataframe[
                candidate
            ].mean()

        )

    return result


# =========================================================
# 무지지자 평균
# =========================================================

def average_undecided(
    dataframe
):

    if len(dataframe) == 0:

        return 0.0

    return float(

        dataframe[
            "undecided"
        ].mean()

    )


# =========================================================
# 최신 무당층 선호 추출
# =========================================================

def latest_undecided_preferences(
    dataframe,
    candidate_names
):
    """
    가장 최근 조사 기준
    무당층 선호 사용
    """

    if len(dataframe) == 0:

        return {}

    latest_row = dataframe.iloc[
        -1
    ]

    result = {}

    for candidate in candidate_names:

        result[candidate] = float(

            latest_row[
                f"{candidate}_pref"
            ]

        )

    return result


# =========================================================
# 데이터 유효성 검사
# =========================================================

def validate_dataframe(
    dataframe,
    candidate_names
):

    errors = []

    if len(dataframe) < 2:

        errors.append(
            "최소 2개 이상의 여론조사가 필요합니다."
        )

    for candidate in candidate_names:

        if candidate not in dataframe.columns:

            errors.append(
                f"{candidate} 컬럼이 없습니다."
            )

    if "sample_size" not in dataframe.columns:

        errors.append(
            "sample_size 컬럼이 없습니다."
        )

    if "undecided" not in dataframe.columns:

        errors.append(
            "undecided 컬럼이 없습니다."
        )

    return errors


# =========================================================
# 시뮬레이터 입력 준비
# =========================================================

def build_simulator_inputs(
    project
):
    """
    app.py에서 바로 사용

    반환

    {
        dataframe,
        candidate_names,
        undecided_preferences
    }
    """

    dataframe = project_to_dataframe(
        project
    )

    preferences = (
        latest_undecided_preferences(
            dataframe,
            project.candidate_names
        )
    )

    return {

        "dataframe":
            dataframe,

        "candidate_names":
            project.candidate_names,

        "undecided_preferences":
            preferences
    }
