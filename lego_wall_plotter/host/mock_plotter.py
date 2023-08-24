import math

from lego_wall_plotter.host.base_types import (
    MotorInstructionsPack,
    MotorInstruction,
    MotorDegrees,
    BoardPack,
    BoardPoint,
    RopeLengths
)
from lego_wall_plotter.host.constants import Constants
from lego_wall_plotter.host.make_motor_instructions import get_initial_degrees


"""
The Mock Plotter basically reverses the operations of "make_motor_instructions",
just to verify whether our logic (both ways) is sound,
and produces what we envisioned.
While the mock plotting code works much different from how the robot works, 
it is a model of what we think the robot should work like, if we could ignore pwm management.
"""


class MotorInstructionReader:
    def __init__(self, filename):
        self._file = open( filename, 'r' )
        self.n_paths = int( self._file.readline().strip() )

    def paths(self):
        for _ in range( self.n_paths ):
            yield PathReader( self._file )
        return


class PathReader:
    def __init__(self, file):
        self._file = file

    def instructions(self):
        while True:
            line = self._file.readline().strip()
            if not line:
                return
            instruction = MotorInstruction( *map( float, line.split(',') ) )
            yield instruction


def _get_intersections( x0, y0, r0, x1, y1, r1 ) :
    # circle 1: (x0, y0), radius r0
    # circle 2: (x1, y1), radius r1

    d = math.sqrt( (x1 - x0) ** 2 + (y1 - y0) ** 2 ) - 0.00001

    # non-intersecting
    if d > r0 + r1 :
        return None
    # One circle within other
    if d < abs( r0 - r1 ) :
        return None
    # coincident circles
    if d == 0 and r0 == r1 :
        return None
    else :
        a = (r0 ** 2 - r1 ** 2 + d ** 2) / (2 * d)
        h = math.sqrt( r0 ** 2 - a ** 2 )
        x2 = x0 + a * (x1 - x0) / d
        y2 = y0 + a * (y1 - y0) / d
        x3 = x2 + h * (y1 - y0) / d
        y3 = y2 - h * (x1 - x0) / d

        x4 = x2 - h * (y1 - y0) / d
        y4 = y2 + h * (x1 - x0) / d

        return (x3, y3, x4, y4)


def _get_point_in_board_space_for_rope_lengths( rope_lengths : RopeLengths ) -> BoardPoint:
    # Note that we are working in anchor space, not board space!!!
    left_anchor = (0, 0)
    right_anchor = (
        Constants.RIGHT_ANCHOR_OFFSET_TO_BOARD_MM[ 0 ] - Constants.LEFT_ANCHOR_OFFSET_TO_BOARD_MM[ 0 ],
        Constants.RIGHT_ANCHOR_OFFSET_TO_BOARD_MM[ 1 ] - Constants.LEFT_ANCHOR_OFFSET_TO_BOARD_MM[ 1 ],
    )

    intersections = _get_intersections(
        *left_anchor, rope_lengths[0],
        *right_anchor, rope_lengths[1]
    )

    i1x, i1y, i2x, i2y = intersections
    if i1x > 0 and i1y > 0:
        x, y = i1x, i1y
    else:
        x, y = i2x, i2y

    # Now that we have worked in anchor space, and will now convert to board space
    return BoardPoint(
        x + Constants.LEFT_ANCHOR_OFFSET_TO_BOARD_MM[ 0 ],
        y + Constants.LEFT_ANCHOR_OFFSET_TO_BOARD_MM[ 1 ]
    )


def _get_target_rope_lengths_for_motor_instruction( motor_instruction : MotorInstruction, initial_degrees : MotorDegrees ) -> RopeLengths:
    return RopeLengths((
        ( motor_instruction.target_degrees_left + initial_degrees[ 0 ] ) * Constants.MM_PER_DEGREE,
        ( motor_instruction.target_degrees_right + initial_degrees[ 1 ] ) * Constants.MM_PER_DEGREE
    ))


def make_plot_pack_for_motor_instructions_file( motor_instructions_file_path : str ) -> BoardPack:

    instruction_reader = MotorInstructionReader( motor_instructions_file_path )

    initial_degrees = get_initial_degrees()
    board_pack = [ ]
    for motor_instruction_path in instruction_reader.paths():
        board_path = [ ]
        for motor_instruction in motor_instruction_path.instructions():

            # compute plot point
            target_rope_lengths = _get_target_rope_lengths_for_motor_instruction( motor_instruction, initial_degrees )
            target_position = _get_point_in_board_space_for_rope_lengths( target_rope_lengths )

            # update result
            board_path.append( target_position )

        board_pack.append( board_path )
    return board_pack
