import math
import logging

from lego_wall_plotter.host.constants import Constants, get_initial_position
from lego_wall_plotter.host.motor_instructions import MotorInstruction, PlotPack


"""
Here we use PlotPacks to create MotorInstructionsPack for the Device
"""


def distance( v1, v2 ) :
    return math.sqrt(
        ((v1[ 0 ] - v2[ 0 ]) ** 2) +
        ((v1[ 1 ] - v2[ 1 ]) ** 2)
    )


def sign( v ) -> int:
    return ( v > 0 ) - ( v < 0 )


def get_rope_length_deltas_mm( current_position, target_position ) :
    # note that positions are in canvas space
    # rope lengths are in anchor space
    # Note that we are working in anchor space, not board space
    left_anchor = (0, 0)
    right_anchor = (
        Constants.RIGHT_ANCHOR_OFFSET[ 0 ] - Constants.LEFT_ANCHOR_OFFSET[ 0 ],
        Constants.RIGHT_ANCHOR_OFFSET[ 1 ] - Constants.LEFT_ANCHOR_OFFSET[ 1 ],
    )

    current_position_in_canvas_space = current_position + Constants.CANVAS_OFFSET_MM
    current_distance_to_left_anchor = distance( current_position_in_canvas_space, left_anchor )
    current_distance_to_right_anchor = distance( current_position_in_canvas_space, right_anchor )

    target_position_in_canvas_space = target_position + Constants.CANVAS_OFFSET_MM
    target_distance_to_left_anchor = distance( target_position_in_canvas_space, left_anchor )
    target_distance_to_right_anchor = distance( target_position_in_canvas_space, right_anchor )

    delta_left_anchor = target_distance_to_left_anchor - current_distance_to_left_anchor
    delta_right_anchor = target_distance_to_right_anchor - current_distance_to_right_anchor

    return delta_left_anchor, delta_right_anchor


def get_motor_instruction_for_rope_lengths( delta_left_anchor, delta_right_anchor ):

    abs_delta_left_anchor = abs( delta_left_anchor )
    abs_delta_right_anchor = abs( delta_right_anchor )

    # first we need to determine relative speeds
    # we will fix the signs afterward!
    # We will set the motor for the larger distance at max speed,
    # and set the speed for the other motor proportionally

    if abs_delta_left_anchor < abs_delta_right_anchor:
        left_speed = round( ( abs_delta_left_anchor / abs_delta_right_anchor ) * 100 )
        right_speed = 100
        duration = abs_delta_right_anchor / Constants.ROPE_LENGTH_PER_ONE_MAX_POWER_SECOND_MM
    else :
        left_speed = 100
        right_speed = round( ( abs_delta_right_anchor / abs_delta_left_anchor ) * 100 )
        duration = abs_delta_left_anchor / Constants.ROPE_LENGTH_PER_ONE_MAX_POWER_SECOND_MM

    left_speed *= sign( delta_left_anchor )
    right_speed *= sign( delta_right_anchor )

    # Due to rounding errors we might not end up at exactly the right position
    # We compensate for the error or subsequent updates, so that it least does not accumulate
    # However, we are still only computing what our position should be,
    # If the motors are not exactly producing the expected rotations,
    # these computed numbers might still differ from reality.
    left_distance = ( left_speed / 100 ) * Constants.ROPE_LENGTH_PER_ONE_MAX_POWER_SECOND_MM * duration
    right_distance = ( right_speed / 100 ) * Constants.ROPE_LENGTH_PER_ONE_MAX_POWER_SECOND_MM * duration
    rope_delta = ( left_distance, right_distance )

    motor_instruction = MotorInstruction(
        left_speed = left_speed,
        right_speed = right_speed,
        duration = duration
    )

    return motor_instruction, rope_delta


def get_intersections( x0, y0, r0, x1, y1, r1 ) :
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


def use_rope_delta_to_determine_actual_position( current_position, rope_delta ) :
    # Note that we are working in anchor space, not board space
    left_anchor = (0, 0)
    right_anchor = (
        Constants.RIGHT_ANCHOR_OFFSET[ 0 ] - Constants.LEFT_ANCHOR_OFFSET[ 0 ],
        Constants.RIGHT_ANCHOR_OFFSET[ 1 ] - Constants.LEFT_ANCHOR_OFFSET[ 1 ],
    )

    current_position_in_canvas_space = current_position + Constants.CANVAS_OFFSET_MM
    current_distance_to_left_anchor = distance( current_position_in_canvas_space, left_anchor )
    current_distance_to_right_anchor = distance( current_position_in_canvas_space, right_anchor )

    new_distance_to_left_anchor = current_distance_to_left_anchor + rope_delta[ 0 ]
    new_distance_to_right_anchor = current_distance_to_right_anchor + rope_delta[ 1 ]

    intersections = get_intersections( *left_anchor, new_distance_to_left_anchor, *right_anchor,
                                       new_distance_to_right_anchor )
    i1x, i1y, i2x, i2y = intersections
    if i1x > 0 and i1y > 0 :
        return i1x, i1y
    else :
        return i2x, i2y


def convert_normalized_point_to_anchor_space( point ) :
    min_extent = min( Constants.CANVAS_SIZE_MM ) - 2 * Constants.PADDING_MM
    min_x = (0.5 * Constants.CANVAS_SIZE_MM[ 0 ]) - (0.5 * min_extent)
    min_y = (0.5 * Constants.CANVAS_SIZE_MM[ 1 ]) - (0.5 * min_extent)

    point_canvas_space = (
        min_x + point[ 0 ] * min_extent + Constants.CANVAS_OFFSET_MM[ 0 ],
        min_y + point[ 1 ] * min_extent + Constants.CANVAS_OFFSET_MM[ 1 ]
    )
    return point_canvas_space


def make_motor_instructions_for_plot_pack( plot_pack : PlotPack ):
    position = get_initial_position()
    motor_instructions_pack = [ ]
    for i_plot_path, plot_path in enumerate( plot_pack ):
        motor_instructions_path = [ ]
        for i_plot_point, plot_point in enumerate( plot_path ):

            # determine target position
            target_position = convert_normalized_point_to_anchor_space( plot_point )

            # get motor settings
            target_distance = distance( position, target_position )
            deltas = get_rope_length_deltas_mm( position, target_position )
            motor_instruction, rope_delta = get_motor_instruction_for_rope_lengths( *deltas )

            # update position
            new_position = use_rope_delta_to_determine_actual_position( position, rope_delta )
            position = new_position

            # check some errors

            min_distance_threshold = 10
            if target_distance < min_distance_threshold:
                logging.info( "-" * 64 )
                logging.info( f"Distance {target_distance} < {min_distance_threshold}, perhaps you need to use a larger sampling_distance! Found in in plot_path {i_plot_path}, plot_point {i_plot_point}" )

            error = distance( new_position, target_position )
            if error > 1:
                logging.info( "-" * 64 )
                logging.info( f"Error > 1 in plot_path {i_plot_path}, plot_point {i_plot_point}" )
                logging.info( f"Target Distance: {target_distance} mm!" )
                logging.info( f"Duration: {motor_instruction.duration} s!" )
                logging.info( f"Move is off by {distance( new_position, target_position )} mm!" )

            motor_instructions_path.append( motor_instruction )
        motor_instructions_pack.append( motor_instructions_path )
    return motor_instructions_pack