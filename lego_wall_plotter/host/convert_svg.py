import logging
import math

from svgpathtools import svg2paths, Path

from lego_wall_plotter.host.base_types import PlotPack


"""
Functions that help convert arbitrary SVG files to a format we can easily work with: PlotPack.
"""

#todo: This code would be easier to work with, if we would first translate the SVG to world-space(board-space)


def get_continuous_paths_from_file( file ) -> list[ Path ]:

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


def make_plot_pack_from_svg_paths( paths : list[ Path ], sampling_distance : float ) -> PlotPack:

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
                path_result[-1] = (x, y)
            else:
                path_result.append((x, y))

        logging.info( f"Parsing path {index + 1}/{len( paths )} - DONE. The path has {len(path_result)} points." )
        point_based_paths.append( path_result )

    return point_based_paths


def make_normalized_paths( paths : PlotPack, n_digits : int ) -> PlotPack:
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

    # rescale to [0, 1]
    normalized_paths = []
    for index, path in enumerate( paths ) :
        logging.info( f"Normalizing path {index + 1}/{len( paths )}" )
        new_path = []
        for point in path :
            new_x = round( ( point[ 0 ] - min_x ) / max_x, n_digits )
            new_y = round( ( point[ 1 ] - min_y ) / max_y, n_digits )
            new_path.append( ( new_x, new_y ) )
        normalized_paths.append( new_path )

    logging.info( f"Normalizing paths - DONE!" )
    return normalized_paths


def sort_paths_by_successive_distance( paths : PlotPack ) -> PlotPack:
    # sort paths by distance between end of path n and start of path n+1
    # the reason to do this is to minimize travel distance,
    # which minimizes time, and room for error
    # We simply take the last element,
    # and then greedily add the rest

    logging.info( "Sorting paths." )
    result_sorted = [ paths.pop() ]
    while len( paths ) > 0 :
        logging.info( "Sort paths, {} left.".format( len( paths ) ) )
        last_added = result_sorted[ -1 ]

        def distance_to_last( p ) :
            return math.sqrt(
                (last_added[ -1 ][ 0 ] - p[ 0 ][ 0 ]) ** 2 + (last_added[ -1 ][ 1 ] - p[ 0 ][ 1 ]) ** 2 )

        closest_path = sorted( paths, key = distance_to_last )[ 0 ]

        result_sorted.append( closest_path )
        paths.remove( closest_path )

    logging.info( "Sorting paths - DONE!" )
    return result_sorted


def convert_svg_file_to_plot_pack( file : str, sampling_distance : float, precision : int ) -> PlotPack:
    # every path in the result will be a continuously connected series of points
    paths = get_continuous_paths_from_file( file )
    paths_point_based = make_plot_pack_from_svg_paths( paths, sampling_distance )
    paths_normalized = make_normalized_paths( paths_point_based, precision )
    paths_sorted = sort_paths_by_successive_distance( paths_normalized )
    return paths_sorted
