import logging
from os import getcwd

from svgpathtools import Path, Line, disvg

from lego_wall_plotter.host.constants import Constants
from lego_wall_plotter.host.motor_instructions import MotorInstructionsPack, PlotPack
from lego_wall_plotter.host.mock_plotter import make_plot_pack_from_motor_instructions_pack


"""
Functions for previewing our PlotPacks and MotorInstructionsPack results.
Useful to make sure you do not let the Device draw something you do not like, 
by checking the previews beforehand. 
"""


def get_board():
    board_paths = [[
        ( 0, 0 ),
        ( Constants.BOARD_SIZE[0], 0 ),
        ( Constants.BOARD_SIZE[0], Constants.BOARD_SIZE[1] ),
        ( 0, Constants.BOARD_SIZE[1] ),
        ( 0, 0 )
    ]]
    return board_paths


def get_anchors():
    anchor_padding = 2
    anchor_padding_offsets = [
        ( -anchor_padding, -anchor_padding ),
        (  anchor_padding, -anchor_padding ),
        (  anchor_padding,  anchor_padding ),
        ( -anchor_padding,  anchor_padding ),
        ( -anchor_padding, -anchor_padding ),
    ]
    left_anchor_paths = []
    for offset in anchor_padding_offsets:
        left_anchor_paths.append(
            (
                Constants.LEFT_ANCHOR_OFFSET[ 0 ] + offset[ 0 ],
                Constants.LEFT_ANCHOR_OFFSET[ 1 ] + offset[ 1 ]
            )
        )
    right_anchor_paths = [ ]
    for offset in anchor_padding_offsets :
        right_anchor_paths.append(
            (
                Constants.RIGHT_ANCHOR_OFFSET[ 0 ] + offset[ 0 ],
                Constants.RIGHT_ANCHOR_OFFSET[ 1 ] + offset[ 1 ]
            )
        )
    anchor_paths = [ left_anchor_paths, right_anchor_paths ]
    return anchor_paths


def get_canvas():
    canvas_paths = [ [
        Constants.CANVAS_OFFSET_MM,
        (
            Constants.CANVAS_OFFSET_MM[ 0 ] + Constants.CANVAS_SIZE_MM[ 0 ],
            Constants.CANVAS_OFFSET_MM[ 1 ]
        ),
        (
            Constants.CANVAS_OFFSET_MM[ 0 ] + Constants.CANVAS_SIZE_MM[ 0 ],
            Constants.CANVAS_OFFSET_MM[ 1 ] + Constants.CANVAS_SIZE_MM[ 1 ]
        ),
        (
            Constants.CANVAS_OFFSET_MM[ 0 ],
            Constants.CANVAS_OFFSET_MM[ 1 ] + Constants.CANVAS_SIZE_MM[ 1 ]
        ),
        Constants.CANVAS_OFFSET_MM
    ] ]
    return canvas_paths


def make_preview_for_plot_pack( plot_pack : PlotPack, out_filename : str ) -> None:
    # create preview svg
    preview = [ ]
    logging.info( f"Writing preview file of converted SVG to {out_filename}." )
    for plot_path in plot_pack :
        preview_p = Path()
        preview.append( preview_p )
        p0 = plot_path[ 0 ]
        for p1 in plot_path[ 1 : ] :
            preview_p.append( Line( complex( p0[0], p0[1] ), complex( p1[0], p1[1] ) ) )
            p0 = p1

    disvg( paths = preview, filename = f"{getcwd()}/{out_filename}", margin_size = 0 )
    logging.info( f"Writing preview file {out_filename} - DONE!" )


def make_preview_for_motor_instructions( motor_instructions_pack : MotorInstructionsPack, out_filename : str ) -> None:
    board = get_board()
    anchors = get_anchors()
    canvas = get_canvas()
    plot = make_plot_pack_from_motor_instructions_pack( motor_instructions_pack )

    # Combine all previous components to define the full scene
    full_plot_pack = board + anchors + canvas + plot

    make_preview_for_plot_pack( full_plot_pack, out_filename )