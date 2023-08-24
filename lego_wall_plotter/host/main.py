import logging
from pathlib import Path
import shutil

from lego_wall_plotter.host.constants import Constants
from lego_wall_plotter.host.convert_svg import convert_svg_file_to_canvas_pack
from lego_wall_plotter.host.make_motor_instructions import make_motor_instructions_for_canvas_pack
from lego_wall_plotter.host.make_preview import make_preview_for_motor_instructions, make_preview_for_pack
from lego_wall_plotter.host.motor_instructions_file import write_motor_instructions_file


"""
Main entrypoint for converting SVGs to instructions for the Device!
"""


def make_motor_instructions(
        in_path_svg : str,
        projects_root_directory : str,
        project_name : str,
) -> None:

    # make sure we have a project directory and that it is empty
    project_directory = Path(f'{projects_root_directory}/{project_name}' )
    project_directory.mkdir(exist_ok = True)
    assert not any(project_directory.iterdir())

    # copy the original svg for future reference
    shutil.copy( in_path_svg, project_directory )

    # make all output file paths
    out_path_scaled_svg = f'{project_directory}/scaled_svg.svg'
    out_path_preview_point_based_svg = f'{project_directory}/point_based.svg'
    out_path_motor_instructions = f'{project_directory}/motor_instructions.txt'
    out_path_mock_preview = f'{project_directory}/mock_preview.svg'

    # Take the SVG and convert it to our own format: CanvasPack
    canvas_pack = convert_svg_file_to_canvas_pack( in_path_svg, Constants.SAMPLING_DISTANCE )

    # Create a preview of the converted SVG
    # ( This should be a piecewise linear approximation of the original )
    make_preview_for_pack( canvas_pack, out_path_preview_point_based_svg )

    # Convert the PlotPack to a MotorInstructionsPack
    motor_instructions_pack = make_motor_instructions_for_canvas_pack( canvas_pack )

    # Write the MotorInstructionsTuplePack to a file for easy copying and archiving reasons
    write_motor_instructions_file( motor_instructions_pack, out_path_motor_instructions )

    # Create a preview of what the MotorInstructionsPack should produce
    # ( should be an approximation of the previous preview, but with some error from rounding and motor limitations )
    make_preview_for_motor_instructions( out_path_motor_instructions, out_path_mock_preview )

    logging.info( "Done!" )
    # You should now manually copy the content of <out_file_motor_instructions_pack>
    # and paste it inside the device code in the MINDSTORMS app.
    # Then move the device code onto the device,
    # and finally let your device execute the instructions!


if __name__ == "__main__" :
    logging.basicConfig( level = logging.INFO )
    projects_root_directory = f'../../out/'
    name = "buffalo"
    make_motor_instructions(
        in_path_svg =  f'../../in/{name}.svg',
        projects_root_directory = projects_root_directory,
        project_name = name
    )
