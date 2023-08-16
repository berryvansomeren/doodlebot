from typing import NewType

from lego_wall_plotter.host.constants import Constants

"""
These are the datastructures we like working with as a fundamental basis of our workflow.
"""

# ----------------------------------------------------------------
PlotPoint = NewType( 'PlotPoint', tuple[ float, float ] )
PlotPath = list[ PlotPoint ]
PlotPack = list[ PlotPath ]

# ----------------------------------------------------------------
class CanvasPoint:
    def __init__(self, x : float, y : float ):
        self.x = x
        self.y = y

        # make sure the coordinates are valid
        for i, v in enumerate( [ self.x, self.y ] ) :
            assert (
                0
                <= v
                < Constants.CANVAS_SIZE_MM[ i ]
            )

# ----------------------------------------------------------------
class BoardPoint:
    def __init__(self, x : float, y : float ):
        self.x = x
        self.y = y

        # make sure the coordinates are valid
        for i, v in enumerate( [ self.x, self.y ] ) :
            assert (
                0
                <= v
                < Constants.BOARD_SIZE_MM[ i ]
            )


MotorDegrees = NewType( 'MotorDegrees', tuple[ float, float ] )
RopeLengths = NewType( 'RopeLengths', tuple[ float, float ] )

# ----------------------------------------------------------------
# These types will be used in device code, so we stick to basic tuples for simpler typing

MotorInstruction = tuple[ int, int ]
MotorInstructionsPath = list[ MotorInstruction ]
MotorInstructionsPack = list[ MotorInstructionsPath ]