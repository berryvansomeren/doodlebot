from lego_wall_plotter.host.constants import Constants, get_initial_position
from lego_wall_plotter.host.motor_instructions import MotorInstructionsPack, MotorInstruction, PlotPack, PlotPoint
from lego_wall_plotter.host.make_motor_instructions import use_rope_delta_to_determine_actual_position


"""
The Mock Plotter should produce results like the LEGO plotter would,
but as a safe virtual SVG, instead of wasting actual paper and manual effort. 
"""


def determine_new_position_after_motor_instruction( current_position : PlotPoint, motor_instruction : MotorInstruction ) -> PlotPoint:
    left_distance = (
        ( motor_instruction.left_speed / 100 )
        * Constants.ROPE_LENGTH_PER_ONE_MAX_POWER_SECOND_MM
        * motor_instruction.duration
    )
    right_distance = (
        ( motor_instruction.right_speed / 100 )
        * Constants.ROPE_LENGTH_PER_ONE_MAX_POWER_SECOND_MM
        * motor_instruction.duration
    )
    rope_delta = (left_distance, right_distance)
    new_position = use_rope_delta_to_determine_actual_position( current_position, rope_delta )
    return new_position


class MockPlotter :
    def __init__( self ):
        self.position = get_initial_position()

    def move( self, motor_instruction : MotorInstruction ) -> PlotPoint:
        new_position = determine_new_position_after_motor_instruction( self.position, motor_instruction )
        self.position = new_position
        return new_position

    def plot( self, motor_instruction_pack : MotorInstructionsPack ) -> PlotPack:
        plot_pack = [ ]
        for motor_instruction_path in motor_instruction_pack :
            current_plot_path = []
            for motor_instruction in motor_instruction_path:
                new_position = self.move( motor_instruction )
                current_plot_path.append( new_position )
            plot_pack.append( current_plot_path )
        return plot_pack


def make_plot_pack_from_motor_instructions_pack( motor_instructions_pack : MotorInstructionsPack ) -> PlotPack:
    plotter = MockPlotter()
    plot_pack = plotter.plot( motor_instructions_pack )
    return plot_pack