from dataclasses import dataclass
from typing import Dict


@dataclass
class World:

    world_id: int

    final_supports: Dict[str, float]

    winner: str

    probability: float = 0.0
