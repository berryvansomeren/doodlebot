import math
import time

import hub

"""
LEGO Plotter

I tried to keep the lego plotter as simple as possible.
All motor instructions for the LEGO plotter are precomputed on the host!
The motor instructions should be copied from the host and pasted into the code below.
"""


MOTOR_INSTRUCTIONS_PACK = [[(144.73324181680437, -393.6555016469647), (450.42959907450495, 2498.368468350509), (-83.31200982265364, 2458.191737792902), (-2394.468174093414, 2260.5034524598086), (-2977.6072068761205, 2158.197343501408), (-3518.6077124218937, 1860.0997041807168), (-3927.9073434061647, 1403.7807510172606), (-4133.5618879777685, 852.1670051226101), (-4097.772483372602, 285.12200590436987), (-3830.133125746863, -209.5516535992283), (-3379.4266693917452, -548.8549510943667), (-2824.833772775215, -671.9920843857508), (-2699.667332263154, -1197.1649991023332), (-2391.134854837721, -1669.4251179515486), (-1915.1700468581294, -1971.0953863771247), (-1353.3794850824925, -2046.4372345519187), (-793.1532237173924, -1879.3580311323494), (-316.71383309292287, -1499.9137490555222), (10.605580446084787, -974.9254069072813), (144.73324181680437, -393.6555016469647)]]


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
    MM_PER_DEGREE = 3760 / 137816
    POINT_REACHED_ERROR_ACCEPTANCE_MM = 1
    POINT_REACHED_ERROR_ACCEPTANCE_DEGREES = POINT_REACHED_ERROR_ACCEPTANCE_MM / abs( MM_PER_DEGREE )
    MAGIC_MOTOR_MODE = [ (1, 0), (2, 2), (3, 1), (0, 0) ]


def sleep( seconds ) :
    time.sleep( seconds )


def sign( v ) -> int :
    return (v > 0) - (v < 0)


class LegoPenController :
    def __init__( self ) :
        self.motor = Constants.MOTOR_PEN.motor
        self.motor.mode( Constants.MAGIC_MOTOR_MODE )
        self.stop_drawing()

    def _move_to_position( self, target_position ) :
        dif = target_position - self.motor.get()[ 2 ]
        if abs( dif ) > 5 :
            self.motor.run_for_degrees( abs( dif ), round( math.copysign( Constants.PEN_MOTOR_SPEED, dif ) ) )
            sleep( 1 )

    def start_drawing( self ) :
        self._move_to_position( Constants.PEN_DOWN )

    def stop_drawing( self ) :
        self._move_to_position( Constants.PEN_UP )


class LegoMotorController :
    def __init__( self ) :
        self.motor_left = Constants.MOTOR_LEFT.motor
        self.motor_left.mode( Constants.MAGIC_MOTOR_MODE )

        self.motor_right = Constants.MOTOR_RIGHT.motor
        self.motor_right.mode( Constants.MAGIC_MOTOR_MODE )

    def move( self, motor_instruction ) :
        # motor instructions describe a relative move in degrees,
        # that is used to determine an absolute target motor position in degrees
        target_degrees_left, target_degrees_right = motor_instruction

        while True :
            # determine current position
            current_degrees_left = self.motor_left.get()[ 1 ]
            current_degrees_right = self.motor_right.get()[ 1 ]

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

        # move to the first point of the path before starting to draw the rest
        motor_controller.move( motor_instruction_path[ 0 ] )
        pen_controller.start_drawing()

        # now draw the rest, while the pen is down
        for instruction in motor_instruction_path[ 1: ] :
            motor_controller.move( instruction )

        # move pen up before moving to the beginning of the next path
        pen_controller.stop_drawing()
        sleep( 2.0 )


# Put the robot in place on the board
# measure the offset to the board
# put those values in Constants
# generate motor instructions
# paste the new motor instructions inside the plotter code
# disconnect the hub from the lego robot, and connect it to the pc
# upload your program to your hub
# connect the hub again to the lego robot
# execute the program!
plot_motor_instructions( MOTOR_INSTRUCTIONS_PACK )