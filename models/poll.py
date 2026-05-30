from dataclasses import dataclass, field
from datetime import date
from typing import Dict


@dataclass
class Poll:

    pollster: str

    start_date: date

    end_date: date

    sample_size: int

    support: Dict[str, float] = field(
        default_factory=dict
    )

    undecided: float = 0.0

    undecided_pref: Dict[str, float] = field(
        default_factory=dict
    )

    def validate(self):

        if self.sample_size <= 0:
            raise ValueError(
                "sample_size must be > 0"
            )

        support_sum = sum(
            self.support.values()
        )

        total = (
            support_sum
            +
            self.undecided
        )

        if total > 100.001:
            raise ValueError(
                "support + undecided > 100"
            )

        pref_total = sum(
            self.undecided_pref.values()
        )

        if (
            pref_total > 0
            and
            abs(pref_total - 100) > 0.01
        ):
            raise ValueError(
                "undecided_pref must sum to 100"
            )

        return True

    def to_dict(self):

        return {

            "pollster":
                self.pollster,

            "start_date":
                str(self.start_date),

            "end_date":
                str(self.end_date),

            "sample_size":
                self.sample_size,

            "support":
                self.support,

            "undecided":
                self.undecided,

            "undecided_pref":
                self.undecided_pref
        }
