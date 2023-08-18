from lego_wall_plotter.host.base_types import (
    MotorInstructionsPack,
    MotorInstruction,
    MotorDegrees,
    BoardPoint,
    CanvasPack,
    CanvasPoint,
    RopeLengths,
)
from lego_wall_plotter.host.constants import Constants
from lego_wall_plotter.host.distance import distance


"""
Here we use PlotPacks to create a MotorInstructionsPack for the Device
Every MotorInstruction describes a relative move for the robot. 
It should just have each motor move a specific number of degrees,
to end up at a specific point. 
We do not actually measure whether the robot ends up in the exact absolute position,
but by tracking relative movements precisely, the result should be the same, 
and the code is a lot simpler.
"""


def get_initial_degrees() -> MotorDegrees:
    pen_to_board_mm = BoardPoint(
        Constants.INITIAL_POSITION_MEASURE_POINT_RELATIVE_TO_BOARD_X_MM
        + Constants.PEN_POSITION_RELATIVE_TO_MEASURE_POINT_X_MM,
        Constants.INITIAL_POSITION_MEASURE_POINT_RELATIVE_TO_BOARD_Y_MM
        + Constants.PEN_POSITION_RELATIVE_TO_MEASURE_POINT_Y_MM
    )

    rope_length_left = distance( BoardPoint(*Constants.LEFT_ANCHOR_OFFSET_TO_BOARD_MM), pen_to_board_mm )
    rope_length_right = distance( BoardPoint(*Constants.RIGHT_ANCHOR_OFFSET_TO_BOARD_MM), pen_to_board_mm )

    degrees_left = rope_length_left / Constants.MM_PER_DEGREE
    degrees_right = rope_length_right / Constants.MM_PER_DEGREE

    return MotorDegrees(( degrees_left, degrees_right ))


def get_rope_lengths_for_point( point : BoardPoint ) -> RopeLengths:
    return RopeLengths((
        distance( BoardPoint(*Constants.LEFT_ANCHOR_OFFSET_TO_BOARD_MM), point ),
        distance( BoardPoint(*Constants.RIGHT_ANCHOR_OFFSET_TO_BOARD_MM), point )
    ))


def convert_canvas_point_to_board_point( point_in_canvas_space : CanvasPoint ) -> BoardPoint:
    return BoardPoint(
        Constants.CANVAS_OFFSET_TO_BOARD_MM[ 0 ] + point_in_canvas_space.x,
        Constants.CANVAS_OFFSET_TO_BOARD_MM[ 1 ] + point_in_canvas_space.y,
    )


def get_motor_instruction_for_rope_lengths( rope_lengths : RopeLengths, initial_degrees : MotorDegrees ) -> MotorInstruction:
    return MotorInstruction((
        ( rope_lengths[ 0 ] / Constants.MM_PER_DEGREE ) - initial_degrees[ 0 ],
        ( rope_lengths[ 1 ] / Constants.MM_PER_DEGREE ) - initial_degrees[ 1 ]
    ))


def make_motor_instructions_for_canvas_pack( canvas_pack : CanvasPack ) -> MotorInstructionsPack:
    initial_degrees = get_initial_degrees()
    motor_instructions_pack = [ ]
    for canvas_path in canvas_pack:
        motor_instructions_path = [ ]
        for canvas_point in canvas_path:

            # compute motor instructions
            target_position = convert_canvas_point_to_board_point( canvas_point )
            target_rope_lengths = get_rope_lengths_for_point( target_position )
            motor_instruction = get_motor_instruction_for_rope_lengths( target_rope_lengths, initial_degrees )

            # update result
            motor_instructions_path.append( motor_instruction )

        motor_instructions_pack.append( motor_instructions_path )
    return motor_instructions_pack
