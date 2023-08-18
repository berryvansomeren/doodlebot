import logging
import math

from svgpathtools import svg2paths, Path

from lego_wall_plotter.host.base_types import CanvasPack, CanvasPoint
from lego_wall_plotter.host.constants import Constants
from lego_wall_plotter.host.distance import distance


"""
Functions that help convert arbitrary SVG files to a format we can easily work with: PlotPack.
"""


SVGPathPack = list[list[tuple[ float, float ]]]


def _get_continuous_paths_from_file( file ) -> list[ Path ]:

    # path elements can be discontinuous
    # here we pre-filter them to make every single Path element continuous

    logging.info( f"Parsing file {file}." )
    paths, attributes = svg2paths(file)

    paths_continuous = []
    for disc_path in paths:
        for continued_path in disc_path.continuous_subpaths():
            paths_continuous.append( continued_path )

    logging.info( f"Parsing file {file} - DONE. Got {len(paths_continuous)} paths." )
    return paths_continuous


def _clean_svg_paths( paths : list[ Path ], sampling_distance : float ) -> SVGPathPack:

    # SVGs can contain complex things like Arcs and Curves,
    # Here we convert them all to sequences of points

    point_based_paths = []
    for index, path in enumerate(paths):
        logging.info( f"Parsing path {index + 1}/{len(paths)}." )

        steps = math.ceil( path.length() / sampling_distance )
        if steps == 0:
            continue

        last_slope = math.inf
        path_result = [ ]
        for p in range(0, steps + 1):
            coords = path.point(p / steps)
            x = coords.real
            y = coords.imag

            should_replace = False
            if len(path_result) > 0:
                last_added = path_result[-1]
                slope = math.atan2(y - last_added[1], x - last_added[0])
                should_replace = math.isclose(slope, last_slope, rel_tol=1e-3)
                if should_replace is False:
                    last_slope = slope

            if should_replace:
                path_result[-1] = ( x, y )
            else:
                path_result.append( ( x, y ) )

        logging.info( f"Parsing path {index + 1}/{len( paths )} - DONE. The path has {len(path_result)} points." )
        point_based_paths.append( path_result )

    return point_based_paths


def _make_canvas_pack_from_svg_paths( paths : SVGPathPack ) -> CanvasPack:
    logging.info( f"Normalizing paths." )

    # determine bounds
    min_x = math.inf
    max_x = -math.inf
    min_y = math.inf
    max_y = -math.inf
    for path in paths:
        for point in path:
            x, y = point
            min_x = min( min_x, x )
            max_x = max( max_x, x )
            min_y = min( min_y, y )
            max_y = max( max_y, y )

    # determine scale factor to transform the coordinates to *fit* the target space, while retaining aspect ratio
    # Also see: https://stackoverflow.com/questions/14219552/scale-coordinates-while-maintaining-the-aspect-ratio-in-ios

    source_width = max_x - min_x
    source_height = max_y - min_y

    target_width = Constants.CANVAS_SIZE_MM[ 0 ] - ( 2 * Constants.CANVAS_PADDING_MM )
    target_height = Constants.CANVAS_SIZE_MM[ 1 ] - ( 2 * Constants.CANVAS_PADDING_MM )

    scale_factor_x = target_width / source_width
    scale_factor_y = target_height / source_height
    scale_factor_fit = min( scale_factor_x, scale_factor_y )

    new_width = source_width * scale_factor_fit
    new_height = source_height * scale_factor_fit

    # Apply the transformation to evert point
    normalized_paths = []
    for index, path in enumerate( paths ) :
        logging.info( f"Normalizing path {index + 1}/{len( paths )}" )
        new_path = []
        for point in path :
            new_x = ( ( point[ 0 ] - min_x ) * scale_factor_fit )
            new_y = ( ( point[ 1 ] - min_y ) * scale_factor_fit )

            # Also to center the coordinates wihtin the target space
            new_x = ( Constants.CANVAS_SIZE_MM[ 0 ] / 2 ) - ( new_width / 2 ) + new_x
            new_y = ( Constants.CANVAS_SIZE_MM[ 1 ] / 2) - ( new_height / 2 ) + new_y

            new_path.append( CanvasPoint( new_x, new_y ) )
        normalized_paths.append( new_path )

    logging.info( f"Normalizing paths - DONE!" )
    return normalized_paths


def _sort_paths_by_successive_distance( paths : CanvasPack ) -> CanvasPack:
    # sort paths by distance between end of path n and start of path n+1
    # the reason to do this is to minimize travel distance,
    # which minimizes time, and room for error
    # We simply take the last element,
    # and then greedily add the rest

    logging.info( "Sorting paths." )
    result_sorted = [ paths.pop() ]
    while len( paths ) > 0 :
        logging.info( "Sort paths, {} left.".format( len( paths ) ) )
        last_point_added = result_sorted[ -1 ][ -1 ]

        def distance_to_last( p ) :
            start_of_path = p[ 0 ]
            return distance( last_point_added, start_of_path )

        closest_path = sorted( paths, key = distance_to_last )[ 0 ]

        result_sorted.append( closest_path )
        paths.remove( closest_path )

    logging.info( "Sorting paths - DONE!" )
    return result_sorted


def _check_canvas_pack_quality( canvas_pack : CanvasPack ) -> None:
    last_point = CanvasPoint(
        Constants.INITIAL_POSITION_MEASURE_POINT_RELATIVE_TO_BOARD_X_MM
        + Constants.PEN_POSITION_RELATIVE_TO_MEASURE_POINT_X_MM
        - Constants.CANVAS_OFFSET_TO_BOARD_MM[ 0 ],
        Constants.INITIAL_POSITION_MEASURE_POINT_RELATIVE_TO_BOARD_Y_MM
        + Constants.PEN_POSITION_RELATIVE_TO_MEASURE_POINT_Y_MM
        - Constants.CANVAS_OFFSET_TO_BOARD_MM[ 1 ],
    )

    logging.info( "-" * 64 )
    logging.info( "Checking the quality of produced paths" )
    for i_path, path in enumerate( canvas_pack ):
        for i_point, point in enumerate( path ):
            d = distance( point, last_point )
            if d < Constants.QUALITY_THRESHOLD_DISTANCE_VALUE:
                logging.info( f"Point {i_point + 1}/{len(path)} in Path {i_path + 1}/{len(canvas_pack)} defines a move of distance {d}")
            last_point = point
    logging.info( "Done" )
    logging.info( "-" * 64 )


def convert_svg_file_to_canvas_pack( file : str, sampling_distance : float ) -> CanvasPack:
    # every path in the result will be a continuously connected series of points
    paths = _get_continuous_paths_from_file( file )
    paths_point_based = _clean_svg_paths( paths, sampling_distance )
    canvas_pack = _make_canvas_pack_from_svg_paths( paths_point_based )
    canvas_pack_sorted = _sort_paths_by_successive_distance( canvas_pack )
    _check_canvas_pack_quality( canvas_pack_sorted )
    return canvas_pack_sorted
