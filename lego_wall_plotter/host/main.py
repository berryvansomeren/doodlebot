import argparse
import logging

from lego_wall_plotter.host.motor_instructions import convert_motor_instructions_pack_to_tuple_based
from lego_wall_plotter.host.convert_svg_paths import convert_svg_file_to_plot_pack
from lego_wall_plotter.host.make_motor_instructions import make_motor_instructions_for_plot_pack
from lego_wall_plotter.host.make_preview import make_preview_for_motor_instructions, make_preview_for_plot_pack


"""
Main entrypoint for converting SVGs to instructions for the Device!
"""


def make_motor_instructions(
        in_file_svg : str,
        out_file_preview_converted_svg : str,
        out_file_preview_motor_instructions : str,
        out_file_motor_instructions_pack : str,
        sampling : float = 1,
        precision : int = 4,
) -> None:

    # Take the SVG and convert it to our own format: PlotPack
    plot_pack = convert_svg_file_to_plot_pack( in_file_svg, sampling, precision )

    # Create a preview of the converted SVG
    # ( This should be a piecewise linear approximation of the original )
    make_preview_for_plot_pack( plot_pack, out_file_preview_converted_svg )

    # Convert the PlotPack to a MotorInstructionsPack
    motor_instructions_pack = make_motor_instructions_for_plot_pack( plot_pack )

    # Create a preview of what the MotorInstructionsPack should produce
    # ( should be an approximation of the previous preview, but with some error from rounding and motor limitations )
    make_preview_for_motor_instructions( motor_instructions_pack, out_file_preview_motor_instructions )

    # Transform the MotorInstructionsPack into a slightly simpler format for the Device: MotorInstructionsTuplePack
    device_motor_instructions_pack = convert_motor_instructions_pack_to_tuple_based( motor_instructions_pack )

    # Write the MotorInstructionsTuplePack to a file for easy copying and archiving reasons
    logging.info( "=" * 64 )
    logging.info( f"Writing final motor instructions to file {out_file_motor_instructions_pack}" )
    with open( out_file_motor_instructions_pack, 'w' ) as instructions_file:
        instructions_file.write( str( device_motor_instructions_pack ) )

    logging.info( "Done!" )
    # You should now manually copy the content of <out_file_motor_instructions_pack>
    # and paste it inside the device code in the MINDSTORMS app.
    # Then move the device code onto the device,
    # and finally let your device execute the instructions!


def parse_args():
    parser = argparse.ArgumentParser( description = 'Convert a svg to wallplotter format' )
    parser.add_argument( 'in_file_svg', type = str, help = 'svg file to convert' )
    parser.add_argument( 'out_file_preview_converted_svg', type = str, help = 'preview SVG of converted input SVG' )
    parser.add_argument( 'out_file_preview_motor_instructions', type = str, help = 'preview SVG of motor instruction result' )
    parser.add_argument( 'out_file_motor_instructions_pack', type = str, help = 'motor instructions file to be copied to device' )
    parser.add_argument( '-s', '--sampling', type = float, default = 1, help = 'Path sampling factor. Decreasing gives rougher corners but decreases filesize. Default: 1' )
    # 4 decimals = 1mm precision at 100cm canvas size
    parser.add_argument( '-p', '--precision', type = int, default = 4, help = 'how many decimals in output. Default: 4' )
    args = parser.parse_args()
    return args


# if __name__ == "__main__" :
#     logging.basicConfig( level = logging.INFO )
#     args = parse_args()
#     make_motor_instructions(
#         in_file_svg = args.in_file_svg,
#         out_file_preview_converted_svg = args.out_file_preview_converted_svg,
#         out_file_preview_motor_instructions = args.out_file_preview_motor_instructions,
#         out_file_motor_instructions_pack = args.out_file_motor_instructions_pack,
#         sampling = args.sampling,
#         precision = args.precision,
#     )

if __name__ == "__main__" :
    logging.basicConfig( level = logging.INFO )
    make_motor_instructions(
        in_file_svg = '../../in/heart.svg',
        out_file_preview_converted_svg = '../../out/1_preview_converted.svg',
        out_file_preview_motor_instructions = '../../out/2_preview_motor_instructions.svg',
        out_file_motor_instructions_pack = '../../out/3_motor_instructions.txt',
    )