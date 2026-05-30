from dataclasses import dataclass
from typing import Dict


@dataclass
class ElectionState:

    values: Dict[str, float]

    def total(self):

        return sum(
            self.values.values()
        )

    def normalize(self):

        total = self.total()

        if total <= 0:
            return

        for k in self.values:

            self.values[k] = (
                self.values[k]
                /
                total
            ) * 100

    def get(self, key):

        return self.values.get(
            key,
            0
        )
