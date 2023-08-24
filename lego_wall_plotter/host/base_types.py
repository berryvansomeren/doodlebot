from dataclasses import dataclass
from typing import NewType

from lego_wall_plotter.host.constants import Constants


"""
These are the datastructures we like working with as a fundamental basis of our workflow.
Some classes contain additional validation to ensure valid coordinate space logic
"""


# ----------------------------------------------------------------
class PlotPoint:
    def __init__(self, x : float, y : float ):
        self.x = x
        self.y = y

        # make sure the coordinates are valid
        for i, v in enumerate( [ self.x, self.y ] ) :
            assert ( 0 <= v <= 1 )

PlotPath = list[ PlotPoint ]
PlotPack = list[ PlotPath ]

# ----------------------------------------------------------------
class CanvasPoint:
    def __init__(self, x : float, y : float ):
        self.x = x
        self.y = y

        # make sure the coordinates are valid
        for i, v in enumerate( [ self.x, self.y ] ) :
            # adding the +1 to add some slack to deal with minor errors,
            # resulting from the scaling factor applied to SVGs
            assert ( 0 - 1 <= v < Constants.CANVAS_SIZE_MM[ i ] + 1 )

CanvasPath = list[ CanvasPoint ]
CanvasPack = list[ CanvasPath ]

# ----------------------------------------------------------------
class BoardPoint:
    def __init__(self, x : float, y : float ):
        self.x = x
        self.y = y

        # make sure the coordinates are valid
        for i, v in enumerate( [ self.x, self.y ] ) :
            assert ( 0 <= v <= Constants.BOARD_SIZE_MM[ i ] )

BoardPath = list[ BoardPoint ]
BoardPack = list[ BoardPath ]

# ----------------------------------------------------------------
MotorDegrees = NewType( 'MotorDegrees', tuple[ float, float ] )
RopeLengths = NewType( 'RopeLengths', tuple[ float, float ] )

# ----------------------------------------------------------------
@dataclass
class MotorInstruction:
    target_degrees_left : float
    target_degrees_right : float

MotorInstructionsPath = list[ MotorInstruction ]
MotorInstructionsPack = list[ MotorInstructionsPath ]