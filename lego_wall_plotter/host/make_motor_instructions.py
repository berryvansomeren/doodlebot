import math

from lego_wall_plotter.host.constants import Constants
from lego_wall_plotter.host.base_types import (
    MotorInstructionsPack,
    MotorInstruction,
    MotorDegrees,
    PlotPack,
    PlotPoint,
    BoardPoint,
    RopeLengths,
)


"""
Here we use PlotPacks to create a MotorInstructionsPack for the Device
Every MotorInstruction describes a relative move for the robot. 
It should just have each motor move a specific number of degrees,
to end up at a specific point. 
We do not actually measure whether the robot ends up in the exact absolute position,
but by tracking relative movements precisely, the result should be the same, 
and the code is a lot simpler.
"""


def distance( v1, v2 ) :
    return math.sqrt(
        ((v1[ 0 ] - v2[ 0 ]) ** 2) +
        ((v1[ 1 ] - v2[ 1 ]) ** 2)
    )


def get_initial_degrees() -> MotorDegrees:

    pen_to_board_mm = (
        Constants.INITIAL_POSITION_MEASURE_POINT_RELATIVE_TO_BOARD_X_MM
        + Constants.PEN_POSITION_RELATIVE_TO_MEASURE_POINT_X_MM,
        Constants.INITIAL_POSITION_MEASURE_POINT_RELATIVE_TO_BOARD_Y_MM
        + Constants.PEN_POSITION_RELATIVE_TO_MEASURE_POINT_Y_MM
    )

    rope_length_left = distance(
        Constants.LEFT_ANCHOR_OFFSET_TO_BOARD_MM,
        pen_to_board_mm
    )

    rope_length_right = distance(
        Constants.RIGHT_ANCHOR_OFFSET_TO_BOARD_MM,
        pen_to_board_mm
    )

    degrees_left = rope_length_left / Constants.MM_PER_DEGREE
    degrees_right = rope_length_right / Constants.MM_PER_DEGREE

    return MotorDegrees(( degrees_left, degrees_right ))


def get_rope_lengths_for_point_in_board_space( point_in_board_space : BoardPoint ) -> RopeLengths:
    rope_length_left = distance(
        Constants.LEFT_ANCHOR_OFFSET_TO_BOARD_MM,
        ( point_in_board_space.x, point_in_board_space.y )
    )

    rope_length_right = distance(
        Constants.RIGHT_ANCHOR_OFFSET_TO_BOARD_MM,
        ( point_in_board_space.x, point_in_board_space.y )
    )
    return RopeLengths(( rope_length_left, rope_length_right ))


def convert_normalized_point_to_board_space( point_in_canvas_space : PlotPoint ) -> BoardPoint:
    # min_extent = min( Constants.CANVAS_SIZE_MM ) - ( 2 * Constants.CANVAS_PADDING_MM )
    # min_x = (0.5 * Constants.CANVAS_SIZE_MM[ 0 ]) - (0.5 * min_extent)
    # min_y = (0.5 * Constants.CANVAS_SIZE_MM[ 1 ]) - (0.5 * min_extent)
    #
    # point_in_canvas_space = (
    #     min_x + point[ 0 ] * min_extent,
    #     min_y + point[ 1 ] * min_extent
    # )

    point_in_board_space = BoardPoint(
        Constants.CANVAS_OFFSET_TO_BOARD_MM[ 0 ] + point_in_canvas_space[ 0 ],
        Constants.CANVAS_OFFSET_TO_BOARD_MM[ 1 ] + point_in_canvas_space[ 1 ],
    )
    return point_in_board_space


def get_motor_instruction_for_rope_lengths( rope_lengths : RopeLengths, initial_degrees : MotorDegrees ) -> MotorInstruction:
    return MotorInstruction((
        ( rope_lengths[ 0 ] / Constants.MM_PER_DEGREE ) - initial_degrees[ 0 ],
        ( rope_lengths[ 1 ] / Constants.MM_PER_DEGREE ) - initial_degrees[ 1 ]
    ))


def make_motor_instructions_for_plot_pack( plot_pack : PlotPack ) -> MotorInstructionsPack:
    initial_degrees = get_initial_degrees()
    motor_instructions_pack = [ ]
    for i_plot_path, plot_path in enumerate( plot_pack ):
        motor_instructions_path = [ ]
        for i_plot_point, plot_point in enumerate( plot_path ):

            # compute motor instructions
            target_position = convert_normalized_point_to_board_space( plot_point )
            target_rope_lengths = get_rope_lengths_for_point_in_board_space( target_position )
            motor_instruction = get_motor_instruction_for_rope_lengths( target_rope_lengths, initial_degrees )

            # update result
            motor_instructions_path.append( motor_instruction )

        motor_instructions_pack.append( motor_instructions_path )
    return motor_instructions_pack
