import math
import time

import hub


"""
LEGO Plotter

I tried to keep the lego plotter as simple as possible.
All motor instructions for the LEGO plotter are precomputed on the host!
The motor instructions should be copied from the host and pasted into the code below.
"""


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


class MotorInstruction:
    def __init__( self, target_degrees_left, target_degrees_right ):
        self.target_degrees_left = target_degrees_left
        self.target_degrees_right = target_degrees_right


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

        # self.motor.run_to_position( Constants.PEN_DOWN )

    def start_drawing( self ) :
        self._move_to_position( Constants.PEN_DOWN )

    def stop_drawing( self ) :
        self._move_to_position( Constants.PEN_UP )


class LegoMotorController :
    def __init__( self ) :
        self.motor_left = Constants.MOTOR_LEFT.motor
        self.motor_left.mode( Constants.MAGIC_MOTOR_MODE )
        self.start_pos_left = self.motor_left.get()[ 1 ]

        self.motor_right = Constants.MOTOR_RIGHT.motor
        self.motor_right.mode( Constants.MAGIC_MOTOR_MODE )
        self.start_pos_right = self.motor_right.get()[ 1 ]

    def get_current_degrees( self ):
        return (
            self.motor_left.get()[ 1 ] - self.start_pos_left,
            self.motor_right.get()[ 1 ] - self.start_pos_right
        )

    def move( self, motor_instruction ) :
        # motor instructions describe in an absolute sense,
        # what the degrees should be to be at a certain point.
        while True :
            # determine current position in motor degrees
            current_degrees_left, current_degrees_right = self.get_current_degrees()

            # determine the error
            error_degrees_left = motor_instruction.target_degrees_left - current_degrees_left
            error_degrees_right = motor_instruction.target_degrees_right - current_degrees_right

            # check if we reached our target
            error_degrees = math.sqrt( error_degrees_left ** 2 + error_degrees_right ** 2 )
            if error_degrees <= Constants.POINT_REACHED_ERROR_ACCEPTANCE_DEGREES :
                break

            # we will first ignore the signs because it makes scaling proportionally easier
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


def plot_motor_instructions( motor_instruction_reader ) :

    pen_controller = LegoPenController()
    motor_controller = LegoMotorController()

    for motor_instruction_path in motor_instruction_reader.paths():

        # move to the first point of the path before starting to draw the rest
        instruction_generator = motor_instruction_path.instructions()
        first_point = next( instruction_generator )
        motor_controller.move( first_point )
        pen_controller.start_drawing()

        # now draw the rest, while the pen is down
        for instruction in instruction_generator:
            motor_controller.move( instruction )

        # move pen up before moving to the beginning of the next path
        pen_controller.stop_drawing()
        sleep( 2.0 )


# Put the robot in place on the board
# measure the offset to the board and put those values in Constants
# generate motor instructions with the main host script,
# and paste the new motor instructions inside the plotter code
# disconnect the hub from the lego robot, and connect it to the pc
# upload your program to your hub
# connect the hub again to the lego robot
# execute the program!
plot_motor_instructions( MotorInstructionReader( 'custom/motor_instructions.txt' ) )