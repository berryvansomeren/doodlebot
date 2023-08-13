import math
import time

import hub

"""
LEGO Plotter

I tried to keep the lego plotter as simple as possible.
All motor instructions for the LEGO plotter are precomputed on the host!
The motor instructions should be copied from the host and pasted into the code below.
"""

MOTOR_INSTRUCTIONS_PACK = [[(144.7332418168044, -393.65550164696515), (305.6963572577011, 2892.0239699974736), (-533.741608897157, -40.17673055760645), (-2311.1561642707607, -197.6882853330934), (-583.1390327827055, -102.3061089583997), (-541.0005055457739, -298.09763932069285), (-409.2996309842711, -456.31895316345634), (-205.6545445716027, -551.6137458946487), (35.78940460516524, -567.0449992182388), (267.6393576257405, -494.673659503601), (450.7064563551162, -339.30329749513595), (554.5928966165299, -123.13713329138439), (125.16644051206191, -525.172914716584), (308.5324774254313, -472.2601188492152), (475.9648079795906, -301.67026842557436), (561.7905617756378, -75.34184817479472), (560.2262613651013, 167.07920341956776), (476.4393906244682, 379.4442820768291), (327.31941353900874, 524.9883421482384), (134.12766137071785, 581.2699052603172)]]



class Constants :
    # which ports are the motors connected to
    # Note that A is on the right hand side when the plotter hangs on the wall
    # (because the hub is upside down,
    # which is because then we can easily connect it to the computer without any disassembling)
    # A also pulls on the rope that is on the right hand side,
    # which means the plotter as a whole will also move to the right when A rotates.
    MOTOR_LEFT = hub.port.B# Defined as hub.port because we will use undocumented functions
    MOTOR_RIGHT = hub.port.A# Defined as hub.port because we will use undocumented functions
    MOTOR_PEN = hub.port.C# Defined as hub.port because we will use undocumented functions

    # absolute motor position when drawing / not drawing
    PEN_UP = 0# not drawing
    PEN_DOWN = 180# drawing
    PEN_MOTOR_SPEED = 30# How fast to move pen up/down

    # Motor settings for power control
    POWER_MAX_PERCENTAGE = 1.0# use only XX% of available motor power
    POWER_PER_DEGREE_PER_SECOND = 1 / 9.3# factor to convert from desired deg/s to power that needs to be applied
    MAX_DEG_PER_S = 100 / POWER_PER_DEGREE_PER_SECOND * POWER_MAX_PERCENTAGE

    # Motor settings for positioning
    MM_PER_DEGREE_LEFT = 3760 / 137816
    MM_PER_DEGREE_RIGHT = 3760 / 137816
    POINT_REACHED_ERROR_ACCEPTANCE_MM = 1
    POINT_REACHED_ERROR_ACCEPTANCE_DEGREES = POINT_REACHED_ERROR_ACCEPTANCE_MM / abs( MM_PER_DEGREE_LEFT )

    # define our coordinate spaces
    # The board is a panel of wood which our anchors are nailed into
    # The canvas is a piece of paper taped to the board
    # By setting a padding we modify the drawable space
    # Note that rope lengths and therefore motor degrees always relative to the anchors
    # while PlotPacks and its components are always within "drawable-space".
    # For conversions, we often work via "board-space" as the global space
    BOARD_SIZE_MM = (900, 1250)
    LEFT_ANCHOR_OFFSET_TO_BOARD_MM = (45, 33)
    RIGHT_ANCHOR_OFFSET_TO_BOARD_MM = (865, 33)
    CANVAS_SIZE_MM = (210, 297)
    CANVAS_OFFSET_TO_BOARD_MM = (345, 335)
    CANVAS_PADDING_MM = 2 * 20

    # While we can compute for every point in "canvas-space" target degrees for our motors,
    # it can still be the case that the inner state of the motors is not completely calibrated to the same space
    # By measuring what the motor state is at the beginning of our program,
    # and relating that to the measured position,
    # we can calibrate the motor's internal values.
    # We will measure a designated point on the lego robot itself, because that's easier to do every time.
    # We have measured the offset of the pen with respect to that specific point, once before.
    INITIAL_POSITION_MEASURE_POINT_RELATIVE_TO_BOARD_X_MM = 493
    INITIAL_POSITION_MEASURE_POINT_RELATIVE_TO_BOARD_Y_MM = 473
    PEN_POSITION_RELATIVE_TO_MEASURE_POINT_X_MM = 0# mm
    PEN_POSITION_RELATIVE_TO_MEASURE_POINT_Y_MM = 22# mm

    MAGIC_MOTOR_MODE = [ (1, 0), (2, 2), (3, 1), (0, 0) ]


def sleep( seconds ) :
    time.sleep( seconds )


def beep() :
    pass


def distance( v1, v2 ) :
    return math.sqrt(
        ((v1[ 0 ] - v2[ 0 ]) ** 2) +
        ((v1[ 1 ] - v2[ 1 ]) ** 2)
    )


def sign( v ) -> int :
    return (v > 0) - (v < 0)


def get_initial_degrees() :
    return (
        (Constants.INITIAL_POSITION_MEASURE_POINT_RELATIVE_TO_BOARD_X_MM
        + Constants.PEN_POSITION_RELATIVE_TO_MEASURE_POINT_X_MM) / Constants.MM_PER_DEGREE_LEFT,
        (Constants.INITIAL_POSITION_MEASURE_POINT_RELATIVE_TO_BOARD_Y_MM
        + Constants.PEN_POSITION_RELATIVE_TO_MEASURE_POINT_Y_MM) / Constants.MM_PER_DEGREE_RIGHT,
    )


def get_rope_lengths_for_point_in_board_space( point_in_board_space ) :
    rope_length_left = distance(
        Constants.LEFT_ANCHOR_OFFSET_TO_BOARD_MM,
        point_in_board_space
    )

    rope_length_right = distance(
        Constants.RIGHT_ANCHOR_OFFSET_TO_BOARD_MM,
        point_in_board_space
    )
    return rope_length_left, rope_length_right


class LegoPenController :
    def __init__( self ) :
        self.motor = Constants.MOTOR_PEN.motor
        self.motor.mode( Constants.MAGIC_MOTOR_MODE )
        self.stop_drawing()

    def move_to_position( self, target_position ) :
        dif = target_position - self.motor.get()[ 2 ]
        if abs( dif ) > 5 :
            self.motor.run_for_degrees( abs( dif ), round( math.copysign( Constants.PEN_MOTOR_SPEED, dif ) ) )
            sleep( 1 )

    def start_drawing( self ) :
        self.move_to_position( Constants.PEN_DOWN )

    def stop_drawing( self ) :
        self.move_to_position( Constants.PEN_UP )


class LegoMotorController :
    def __init__( self ) :
        self.motor_left = Constants.MOTOR_LEFT.motor
        self.motor_left.mode( Constants.MAGIC_MOTOR_MODE )

        self.motor_right = Constants.MOTOR_RIGHT.motor
        self.motor_right.mode( Constants.MAGIC_MOTOR_MODE )

        self.initial_degrees = get_initial_degrees()

    def move( self, motor_instruction ) :
        # motor instructions describe a relative move in degrees,
        # that is used to determine an absolute target motor position in degrees
        degrees_left, degrees_right = motor_instruction

        current_degrees_left = self.motor_left.get()[ 1 ] + self.initial_degrees[ 0 ]
        current_degrees_right = self.motor_right.get()[ 1 ] + self.initial_degrees[ 1 ]
        target_degrees_left = current_degrees_left + degrees_left
        target_degrees_right = current_degrees_right + degrees_right

        while True :
            # determine current position
            current_degrees_left = self.motor_left.get()[ 1 ] + self.initial_degrees[ 0 ]
            current_degrees_right = self.motor_right.get()[ 1 ] + self.initial_degrees[ 1 ]

            # determine the error
            error_degrees_left = target_degrees_left - current_degrees_left
            error_degrees_right = target_degrees_right - current_degrees_right

            # check if we reached our target
            error_degrees = math.sqrt( error_degrees_left ** 2 + error_degrees_right ** 2 )
            if error_degrees <= Constants.POINT_REACHED_ERROR_ACCEPTANCE_DEGREES :
                break

            # we will first ignore the signs because it makes scaling proportionally easy
            abs_error_degrees_left = abs( error_degrees_left )
            abs_error_degrees_right = abs( error_degrees_right )

            # one of the motors will run at max dps, while the other is scaled proportionally
            if abs_error_degrees_left < abs_error_degrees_right :
                left_dps = round( (abs_error_degrees_left / abs_error_degrees_right) * Constants.MAX_DEG_PER_S )
                right_dps = Constants.MAX_DEG_PER_S
            else :
                left_dps = Constants.MAX_DEG_PER_S
                right_dps = round( (abs_error_degrees_right / abs_error_degrees_left) * Constants.MAX_DEG_PER_S )

            # we now fix the signs
            left_dps *= sign( error_degrees_left )
            right_dps *= sign( error_degrees_right )

            # update dps
            self.set_degree_per_second( left_dps, right_dps )

        # target reached!
        self.brake()
        sleep( 0.1 )

    def set_degree_per_second( self, left, right ) :
        self.motor_left.pwm( round( left * Constants.POWER_PER_DEGREE_PER_SECOND ) )
        self.motor_right.pwm( round( right * Constants.POWER_PER_DEGREE_PER_SECOND ) )

    def brake( self ) :
        self.set_degree_per_second( 0, 0 )
        self.motor_left.brake()
        self.motor_right.brake()


def plot_motor_instructions( motor_instructions_pack ) :
    pen_controller = LegoPenController()
    motor_controller = LegoMotorController()

    for motor_instruction_path in motor_instructions_pack :

        # Note: MotorInstructionsPack = list[ list[ MotorInstruction ] ]
        # Note: MotorInstruction = tuple[ left_degrees : int, right_degrees : int ]

        # move to the first point of the path before starting to draw the rest
        motor_controller.move( motor_instruction_path[ 0 ] )
        pen_controller.start_drawing()

        # now draw the rest, while the pen is down
        for instruction in motor_instruction_path[ 1: ] :
            beep()
            motor_controller.move( instruction )
            beep()

        # move pen up before moving to the beginning of the next path
        pen_controller.stop_drawing()
        sleep( 2.0 )


# just put the bot in place,
# select the right program
# and press play when ready to start!
beep()
plot_motor_instructions( MOTOR_INSTRUCTIONS_PACK )
beep()