from mindstorms import MSHub, Motor
from mindstorms.control import wait_for_seconds


hub = MSHub()


"""
LEGO Plotter

I tried to keep the lego plotter as simple as possible. 
All motor instructions for the LEGO plotter are precomputed on the host!
The motor instructions should be copied from the host and pasted into the code below.
"""


MOTOR_INSTRUCTIONS_PACK = [[(-46, -100, 5.58922820259783), (9, 100, 3.8946784356815725), (-100, -16, 0.7115967940323424), (-100, -17, 3.1449725188861333), (-100, -27, 0.789415790209285), (-100, -65, 0.7220228603290145), (-80, -100, 0.6741278631223743), (-33, -100, 0.7744507746163382), (8, -100, 0.7626221478720668), (59, -100, 0.6309868589663532), (100, -64, 0.6133581919400044), (100, -11, 0.7536635176497237), (24, -100, 0.6972166797482205), (70, -100, 0.5962884761902588), (100, -53, 0.644534070492448), (100, -3, 0.7620782484753711), (100, 39, 0.7629653309690759), (100, 88, 0.650401772141536), (60, 100, 0.746719489711281), (22, 100, 0.7952523452122678)]]


class Constants:
    # which ports are the motors connected to
    # Note that A is on the right hand side when the plotter hangs on the wall
    # (because the hub is upside down,
    # which is because then we can easily connect it to the computer without any disassembling)
    # A also pulls on the rope that is on the right hand side,
    # which means the plotter as a whole will also move to the right when A rotates.
    MOTOR_LEFT = 'E'
    MOTOR_RIGHT = 'F'
    MOTOR_PEN = 'D'

    # absolute motor position when drawing / not drawing
    PEN_UP = 0  # not drawing
    PEN_DOWN = 180  # drawing
    PEN_MOTOR_SPEED = 30  # How fast to move pen up/down

    # Motor settings for power control
    POWER_MAX_PERCENTAGE = 1.0  # use only XX% of available motor power
    POWER_PER_DEGREE_PER_SECOND = 1 / 9.3  # factor to convert from desired deg/s to power that needs to be applied
    MAX_DEG_PER_S = 100 / POWER_PER_DEGREE_PER_SECOND * POWER_MAX_PERCENTAGE

    # Motor settings for positioning
    MM_PER_DEGREE = 3760 / 137816
    POINT_REACHED_ERROR_ACCEPTANCE_MM = 1
    POINT_REACHED_ERROR_ACCEPTANCE_DEGREES = POINT_REACHED_ERROR_ACCEPTANCE_MM / MM_PER_DEGREE


def sign( v ) -> int:
    return ( v > 0 ) - ( v < 0 )


class LegoPenController:
    def __init__(self):
        self.motor = Motor( Constants.MOTOR_PEN )
        self.motor.set_stop_action('hold')
        self.motor.set_default_speed( Constants.PEN_MOTOR_SPEED )
        self.stop_drawing()

    def start_drawing(self):
        self.motor.run_to_position( Constants.PEN_DOWN )

    def stop_drawing(self):
        self.motor.run_to_position( Constants.PEN_UP )


class LegoMotorController:
    def __init__(self):
        self.motor_left = Motor( Constants.MOTOR_LEFT )
        self.motor_left.set_stop_action( 'hold' )

        self.motor_right = Motor( Constants.MOTOR_RIGHT )
        self.motor_right.set_stop_action( 'hold' )

    def move( self, motor_instruction ):
        # motor instructions describe a target position
        degrees_left, degrees_right = motor_instruction
        while True:
            # determine current position
            current_degrees_left = self.motor_left.get()[ 1 ]
            current_degrees_right = self.motor_right.get()[ 1 ]

            # determine the error
            error_degrees_left = degrees_left - current_degrees_left
            error_degrees_right = degrees_right - current_degrees_right

            # check if we reached our target
            if error_degrees_left == 0 and error_degrees_right == 0:
                self.brake()
                return

            # we will first ignore the signs because it makes scaling proportionally easy
            abs_error_degrees_left = abs( error_degrees_left )
            abs_error_degrees_right = abs( error_degrees_right )

            # one of the motors will run at max dps, while the other is scaled proportionally
            if abs_error_degrees_left < abs_error_degrees_right :
                left_dps = round( ( abs_error_degrees_left / abs_error_degrees_right ) * Constants.MAX_DEG_PER_S )
                right_dps = Constants.MAX_DEG_PER_S
            else :
                left_dps = Constants.MAX_DEG_PER_S
                right_dps = round( ( abs_error_degrees_right / abs_error_degrees_left ) * Constants.MAX_DEG_PER_S )

            # we now fix the signs
            left_dps *= sign( error_degrees_left )
            right_dps *= sign( error_degrees_right )

            # update dps
            self.set_degree_per_second( left_dps, right_dps )

    def set_degree_per_second( self, left, right ):
        self.motor_left.pwm( round( left * Constants.POWER_PER_DEGREE_PER_SECOND ) )
        self.motor_right.pwm( round( right * Constants.POWER_PER_DEGREE_PER_SECOND ) )

    def brake( self ):
        self.set_degree_per_second( 0, 0 )
        self.motor_left.brake()
        self.motor_right.brake()


class LegoPlotter:
    def __init__(self):
        self.pen_controller = LegoPenController()
        self.motor_controller = LegoMotorController()

    def plot(self, motor_instruction_paths):

        # Note: MotorInstructionsPack = list[ list[ MotorInstruction ] ]
        # Note: MotorInstruction = tuple[ left_degrees : int, right_degrees : int ]

        for path in motor_instruction_paths:
            # move to the first point of the path before starting to draw the rest
            self.motor_controller.move( path[0] )
            self.pen_controller.start_drawing()
            # now draw the rest
            for instruction in path[1:]:
                self.motor_controller.move( instruction )
                wait_for_seconds(0.5)
            self.pen_controller.stop_drawing()
            wait_for_seconds(1.0)


# just put the bot in place,
# select the right program
# and press play when ready to start!
hub.speaker.beep()
plotter = LegoPlotter()
plotter.plot( MOTOR_INSTRUCTIONS_PACK )
hub.speaker.beep()