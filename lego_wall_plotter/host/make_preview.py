import logging
from os import getcwd

from svgpathtools import Path, Line, disvg

from lego_wall_plotter.host.constants import Constants
from lego_wall_plotter.host.base_types import MotorInstructionsPack, BoardPack, BoardPoint
from lego_wall_plotter.host.mock_plotter import make_plot_pack_for_motor_instructions


"""
Functions for previewing our PlotPacks and MotorInstructionsPack results.
Useful to make sure you do not let the Device draw something you do not like, 
by checking the previews beforehand. 
"""


def _get_board() -> BoardPack:
    board_paths = [[
        BoardPoint( 0, 0 ),
        BoardPoint( Constants.BOARD_SIZE_MM[ 0 ], 0 ),
        BoardPoint( Constants.BOARD_SIZE_MM[ 0 ], Constants.BOARD_SIZE_MM[ 1 ] ),
        BoardPoint( 0, Constants.BOARD_SIZE_MM[1 ]),
        BoardPoint( 0, 0 )
    ]]
    return board_paths


def _get_anchors() -> BoardPack:
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
            BoardPoint(
                Constants.LEFT_ANCHOR_OFFSET_TO_BOARD_MM[ 0 ] + offset[ 0 ],
                Constants.LEFT_ANCHOR_OFFSET_TO_BOARD_MM[ 1 ] + offset[ 1 ]
            )
        )
    right_anchor_paths = [ ]
    for offset in anchor_padding_offsets :
        right_anchor_paths.append(
            BoardPoint(
                Constants.RIGHT_ANCHOR_OFFSET_TO_BOARD_MM[ 0 ] + offset[ 0 ],
                Constants.RIGHT_ANCHOR_OFFSET_TO_BOARD_MM[ 1 ] + offset[ 1 ]
            )
        )
    anchor_paths = [ left_anchor_paths, right_anchor_paths ]
    return anchor_paths


def _get_canvas() -> BoardPack:
    canvas_paths = [ [
        BoardPoint( *Constants.CANVAS_OFFSET_TO_BOARD_MM ),
        BoardPoint(
            Constants.CANVAS_OFFSET_TO_BOARD_MM[ 0 ] + Constants.CANVAS_SIZE_MM[ 0 ],
            Constants.CANVAS_OFFSET_TO_BOARD_MM[ 1 ]
        ),
        BoardPoint(
            Constants.CANVAS_OFFSET_TO_BOARD_MM[ 0 ] + Constants.CANVAS_SIZE_MM[ 0 ],
            Constants.CANVAS_OFFSET_TO_BOARD_MM[ 1 ] + Constants.CANVAS_SIZE_MM[ 1 ]
        ),
        BoardPoint(
            Constants.CANVAS_OFFSET_TO_BOARD_MM[ 0 ],
            Constants.CANVAS_OFFSET_TO_BOARD_MM[ 1 ] + Constants.CANVAS_SIZE_MM[ 1 ]
        ),
        BoardPoint( *Constants.CANVAS_OFFSET_TO_BOARD_MM )
    ] ]
    return canvas_paths


def make_preview_for_pack( pack, out_filename : str ) -> None:
    # create preview svg
    preview = [ ]
    logging.info( f"Writing preview file of converted SVG to {out_filename}." )
    for path in pack :
        preview_p = Path()
        preview.append( preview_p )
        p0 = path[ 0 ]
        for p1 in path[ 1 : ] :
            preview_p.append( Line( complex( p0.x, p0.y ), complex( p1.x, p1.y ) ) )
            p0 = p1

    disvg( paths = preview, filename = f"{getcwd()}/{out_filename}", margin_size = 0 )
    logging.info( f"Writing preview file {out_filename} - DONE!" )


def make_preview_for_motor_instructions( motor_instructions_pack : MotorInstructionsPack, out_filename : str ) -> None:
    board = _get_board()
    anchors = _get_anchors()
    canvas = _get_canvas()
    plot = make_plot_pack_for_motor_instructions( motor_instructions_pack )

    # Combine all previous components to define the full scene
    full_plot_pack = board + anchors + canvas + plot

    make_preview_for_pack( full_plot_pack, out_filename )