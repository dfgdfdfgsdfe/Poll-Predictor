# =========================================================
# data/models.py
# =========================================================

from dataclasses import dataclass, field, asdict
from typing import Dict, List


# =========================================================
# 단일 여론조사
# =========================================================

@dataclass
class Poll:

    pollster: str

    start_date: str

    end_date: str

    sample_size: int

    supports: Dict[str, float]

    undecided: float

    undecided_preferences: Dict[str, float]

    def to_dict(
        self
    ):
        return asdict(
            self
        )

    @staticmethod
    def from_dict(
        data
    ):

        return Poll(
            pollster=data[
                "pollster"
            ],

            start_date=data[
                "start_date"
            ],

            end_date=data[
                "end_date"
            ],

            sample_size=data[
                "sample_size"
            ],

            supports=data[
                "supports"
            ],

            undecided=data[
                "undecided"
            ],

            undecided_preferences=data[
                "undecided_preferences"
            ]
        )


# =========================================================
# 시뮬레이션 프로젝트
# =========================================================

@dataclass
class ElectionProject:

    project_name: str

    election_date: str

    candidate_names: List[str]

    polls: List[Poll] = field(
        default_factory=list
    )

    def add_poll(
        self,
        poll: Poll
    ):

        self.polls.append(
            poll
        )

    def remove_poll(
        self,
        index: int
    ):

        if (

            0 <= index

            < len(
                self.polls
            )

        ):

            self.polls.pop(
                index
            )

    def to_dict(
        self
    ):

        return {

            "project_name":
                self.project_name,

            "election_date":
                self.election_date,

            "candidate_names":
                self.candidate_names,

            "polls":

                [

                    poll.to_dict()

                    for poll

                    in self.polls

                ]
        }

    @staticmethod
    def from_dict(
        data
    ):

        project = ElectionProject(

            project_name=data[
                "project_name"
            ],

            election_date=data[
                "election_date"
            ],

            candidate_names=data[
                "candidate_names"
            ]
        )

        for poll_data in data[
            "polls"
        ]:

            project.add_poll(

                Poll.from_dict(
                    poll_data
                )

            )

        return project


# =========================================================
# World 결과
# =========================================================

@dataclass
class WorldResult:

    world_id: int

    winner: str

    final_result: Dict[str, float]

    def to_dict(
        self
    ):
        return asdict(
            self
        )

    @staticmethod
    def from_dict(
        data
    ):

        return WorldResult(

            world_id=data[
                "world_id"
            ],

            winner=data[
                "winner"
            ],

            final_result=data[
                "final_result"
            ]
        )


# =========================================================
# 시뮬레이션 결과
# =========================================================

@dataclass
class SimulationResult:

    worlds: list

    prediction_table: dict

    win_rates: dict

    filtered_state: dict

    def to_dict(
        self
    ):

        return {

            "worlds":
                self.worlds,

            "prediction_table":
                self.prediction_table,

            "win_rates":
                self.win_rates,

            "filtered_state":
                self.filtered_state
        }
