import math
from typing import TypeVar


T = TypeVar("T")

def distance( v1 : T, v2 : T ) -> float:
    return math.sqrt(
        ( ( v1.x - v2.x ) ** 2 ) +
        ( ( v1.y - v2.y ) ** 2 )
    )