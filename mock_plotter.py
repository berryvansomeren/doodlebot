import math
import logging
from os import getcwd

from svgpathtools import Path, Line, disvg

class Constants:

    # Canvas
    BOARD_SIZE = ( 900, 1250 )
    LEFT_ANCHOR_OFFSET = ( 45, 33 )
    RIGHT_ANCHOR_OFFSET = ( 865, 33 )
    CANVAS_SIZE_MM = ( 210, 297 )
    CANVAS_OFFSET_MM = ( 345, 335 )
    PADDING_MM = 5 * 10

    # which ports are the motors connected to
    # Note that A is on the right hand side when the plotter hangs on the wall
    # (because the hub is upside down,
    # which is because then we can easily connect it to the computer without any disassembling)
    # A also pulls on the rope that is on the right hand side,
    # which means the plotter as a whole will also move to the right when A rotates.
    MOTOR_LEFT = 'B'
    MOTOR_RIGHT = 'A'
    MOTOR_PEN = 'C'

    # absolute motor position when drawing / not drawing
    PEN_UP = 0  # not drawing
    PEN_DOWN = 180  # drawing
    PEN_MOTOR_SPEED = 30  # How fast to move pen up/down

    # How motor speed affects rope consumption
    # this value is how much mm of rope is consumed by running a motor at 100% speed for one second
    ROPE_LENGTH_PER_ONE_MAX_POWER_SECOND_MM = 1000


def distance( v1, v2 ):
    return math.sqrt(
        ( ( v1[0] - v2[0] ) ** 2 ) +
        ( ( v1[1] - v2[1] ) ** 2 )
    )


def get_rope_length_deltas_mm( current_position, target_position ):

    # note that positions are in canvas space
    # rope lengths are in anchor space
    # Note that we are working in anchor space, not board space
    left_anchor = (0, 0)
    right_anchor = (
        Constants.RIGHT_ANCHOR_OFFSET[ 0 ] - Constants.LEFT_ANCHOR_OFFSET[ 0 ],
        Constants.RIGHT_ANCHOR_OFFSET[ 1 ] - Constants.LEFT_ANCHOR_OFFSET[ 1 ],
    )

    current_position_in_canvas_space = current_position + Constants.CANVAS_OFFSET_MM
    current_distance_to_left_anchor = distance( current_position_in_canvas_space, left_anchor )
    current_distance_to_right_anchor = distance( current_position_in_canvas_space, right_anchor )

    target_position_in_canvas_space = target_position + Constants.CANVAS_OFFSET_MM
    target_distance_to_left_anchor = distance( target_position_in_canvas_space, left_anchor )
    target_distance_to_right_anchor = distance( target_position_in_canvas_space, right_anchor )

    delta_left_anchor = target_distance_to_left_anchor - current_distance_to_left_anchor
    delta_right_anchor = target_distance_to_right_anchor - current_distance_to_right_anchor

    return delta_left_anchor, delta_right_anchor


def get_motor_settings_for_rope_lengths( delta_left_anchor, delta_right_anchor ):

    if delta_left_anchor < delta_right_anchor:
        left_speed = round( ( delta_left_anchor / delta_right_anchor ) * 100 )
        right_speed = 100
        duration = delta_right_anchor / Constants.ROPE_LENGTH_PER_ONE_MAX_POWER_SECOND_MM
    else:
        left_speed = 100
        right_speed = round( ( delta_right_anchor / delta_left_anchor ) * 100 )
        duration = delta_left_anchor / Constants.ROPE_LENGTH_PER_ONE_MAX_POWER_SECOND_MM

    # Due to rounding errors we might not end up at exactly the right position
    # We compensate for the error or subsequent updates, so that it least does not accumulate
    # However, we are still only computing what our position should be,
    # If the motors are not exactly producing the expected rotations,
    # these computed numbers might still differ from reality.
    left_distance = ( left_speed / 100 ) * Constants.ROPE_LENGTH_PER_ONE_MAX_POWER_SECOND_MM * duration
    right_distance = ( right_speed / 100 ) * Constants.ROPE_LENGTH_PER_ONE_MAX_POWER_SECOND_MM * duration
    rope_delta = ( left_distance, right_distance )

    return left_speed, right_speed, duration, rope_delta


def get_intersections( x0, y0, r0, x1, y1, r1 ) :
    # circle 1: (x0, y0), radius r0
    # circle 2: (x1, y1), radius r1

    d = math.sqrt( (x1 - x0) ** 2 + (y1 - y0) ** 2 ) - 0.00001

    # non-intersecting
    if d > r0 + r1 :
        return None
    # One circle within other
    if d < abs( r0 - r1 ) :
        return None
    # coincident circles
    if d == 0 and r0 == r1 :
        return None
    else :
        a = (r0 ** 2 - r1 ** 2 + d ** 2) / (2 * d)
        h = math.sqrt( r0 ** 2 - a ** 2 )
        x2 = x0 + a * (x1 - x0) / d
        y2 = y0 + a * (y1 - y0) / d
        x3 = x2 + h * (y1 - y0) / d
        y3 = y2 - h * (x1 - x0) / d

        x4 = x2 - h * (y1 - y0) / d
        y4 = y2 + h * (x1 - x0) / d

        return (x3, y3, x4, y4)


def use_rope_delta_to_determine_actual_position( current_position, rope_delta ):
    # Note that we are working in anchor space, not board space
    left_anchor = (0, 0)
    right_anchor = (
        Constants.RIGHT_ANCHOR_OFFSET[ 0 ] - Constants.LEFT_ANCHOR_OFFSET[ 0 ],
        Constants.RIGHT_ANCHOR_OFFSET[ 1 ] - Constants.LEFT_ANCHOR_OFFSET[ 1 ],
    )

    current_position_in_canvas_space = current_position + Constants.CANVAS_OFFSET_MM
    current_distance_to_left_anchor = distance( current_position_in_canvas_space, left_anchor )
    current_distance_to_right_anchor = distance( current_position_in_canvas_space, right_anchor )

    new_distance_to_left_anchor = current_distance_to_left_anchor + rope_delta[0]
    new_distance_to_right_anchor = current_distance_to_right_anchor + rope_delta[1]

    intersections = get_intersections( *left_anchor, new_distance_to_left_anchor, *right_anchor, new_distance_to_right_anchor )
    i1x, i1y, i2x, i2y = intersections
    if i1x > 0 and i1y > 0:
        return i1x, i1y
    else:
        return i2x, i2y


def convert_normalized_point_to_anchor_space( point ):
    point_canvas_space = (
        point[ 0 ] * (Constants.CANVAS_SIZE_MM[ 0 ] - 2 * Constants.PADDING_MM) + Constants.CANVAS_OFFSET_MM[ 0 ] + Constants.PADDING_MM,
        point[ 1 ] * (Constants.CANVAS_SIZE_MM[ 1 ] - 2 * Constants.PADDING_MM) + Constants.CANVAS_OFFSET_MM[ 1 ] + Constants.PADDING_MM
    )
    return point_canvas_space


def create_preview_svg( svg_paths: list[ list[ tuple ] ], out_filename: str ) -> None :

    # draw the board
    board_paths = [[
        ( 0, 0 ),
        ( Constants.BOARD_SIZE[0], 0 ),
        ( Constants.BOARD_SIZE[0], Constants.BOARD_SIZE[1] ),
        ( 0, Constants.BOARD_SIZE[1] ),
        ( 0, 0 )
    ]]

    # draw the two anchors
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

    # Draw the canvas space
    canvas_paths = [[
        Constants.CANVAS_OFFSET_MM,
        (
            Constants.CANVAS_OFFSET_MM[0] + Constants.CANVAS_SIZE_MM[0],
            Constants.CANVAS_OFFSET_MM[1]
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
    ]]

    # Combine all previous components to define the full scene
    all_paths = board_paths + anchor_paths + canvas_paths + svg_paths

    # create preview svg
    preview = [ ]
    logging.info( f"Writing preview file {out_filename}." )

    for path in all_paths :
        preview_p = Path()
        preview.append( preview_p )
        p0 = path[ 0 ]
        for p1 in path[ 1 : ] :
            preview_p.append( Line( complex( p0[ 0 ], p0[ 1 ] ), complex( p1[ 0 ], p1[ 1 ] ) ) )
            p0 = p1

    disvg( paths = preview, filename = f"{getcwd()}/{out_filename}", margin_size = 0 )
    logging.info( f"Writing preview file {out_filename} - DONE!" )


class MockPlotter :
    def __init__( self, out_file_name ):
        self.out_file_name = out_file_name
        self.position = 0, 0

    def move_to( self, target_position ) :
        deltas = get_rope_length_deltas_mm( self.position, target_position )
        motor_settings = get_motor_settings_for_rope_lengths( *deltas )
        left_speed, right_speed, duration, rope_delta = motor_settings
        new_position = use_rope_delta_to_determine_actual_position( self.position, rope_delta )
        self.position = new_position
        logging.info( "-" * 64 )
        logging.info( f"Current: {self.position}" )
        logging.info( f"Target: {target_position}" )
        logging.info( f"Move is off by {distance( new_position, target_position )} mm!")


    def plot_paths( self, svg_paths ) :
        plot_paths = [ ]
        for path in svg_paths :
            current_plot_path = []
            for point in path:
                point_in_anchor_space = convert_normalized_point_to_anchor_space( point )
                self.move_to( point_in_anchor_space )
                current_plot_path.append( self.position )
            plot_paths.append( current_plot_path )
        create_preview_svg( plot_paths, self.out_file_name )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    plotter = MockPlotter( "/out/mock.svg" )
    svg_paths = [[(0.9141, 0.546), (0.4997, 0.999), (0.4976, 0.9971), (0.0853, 0.5464), (0.0832, 0.5441), (0.0812, 0.5418), (0.0792, 0.5395), (0.0772, 0.5371), (0.0752, 0.5348), (0.0733, 0.5324), (0.0714, 0.53), (0.0695, 0.5275), (0.0676, 0.5251), (0.0657, 0.5226), (0.0639, 0.5201), (0.0621, 0.5176), (0.0603, 0.5151), (0.0585, 0.5125), (0.0568, 0.5099), (0.055, 0.5073), (0.0533, 0.5047), (0.0517, 0.5021), (0.05, 0.4995), (0.0484, 0.4968), (0.0468, 0.4941), (0.0452, 0.4914), (0.0437, 0.4887), (0.0421, 0.486), (0.0406, 0.4832), (0.0392, 0.4804), (0.0377, 0.4777), (0.0363, 0.4749), (0.0349, 0.472), (0.0335, 0.4692), (0.0322, 0.4664), (0.0308, 0.4635), (0.0295, 0.4606), (0.0283, 0.4577), (0.027, 0.4548), (0.0258, 0.4519), (0.0246, 0.449), (0.0235, 0.4461), (0.0223, 0.4431), (0.0212, 0.4401), (0.0201, 0.4372), (0.0191, 0.4342), (0.0181, 0.4312), (0.0171, 0.4282), (0.0161, 0.4251), (0.0151, 0.4221), (0.0142, 0.4191), (0.0133, 0.416), (0.0125, 0.413), (0.0117, 0.4099), (0.0108, 0.4068), (0.0101, 0.4037), (0.0093, 0.4006), (0.0086, 0.3975), (0.0079, 0.3944), (0.0073, 0.3913), (0.0066, 0.3882), (0.006, 0.385), (0.0054, 0.3819), (0.0049, 0.3787), (0.0044, 0.3756), (0.0039, 0.3724), (0.0034, 0.3693), (0.003, 0.3661), (0.0026, 0.3629), (0.0022, 0.3597), (0.0019, 0.3566), (0.0016, 0.3534), (0.0013, 0.3502), (0.001, 0.347), (0.0008, 0.3438), (0.0006, 0.3406), (0.0004, 0.3374), (0.0003, 0.3342), (0.0002, 0.331), (0.0001, 0.3278), (0.0, 0.3246), (0.0, 0.3214), (0.0, 0.3182), (0.0, 0.315), (0.0001, 0.3118), (0.0002, 0.3086), (0.0003, 0.3054), (0.0005, 0.3022), (0.0007, 0.299), (0.0009, 0.2958), (0.0011, 0.2926), (0.0014, 0.2894), (0.0017, 0.2862), (0.002, 0.2831), (0.0024, 0.2799), (0.0027, 0.2767), (0.0032, 0.2735), (0.0036, 0.2704), (0.0041, 0.2672), (0.0046, 0.264), (0.0051, 0.2609), (0.0057, 0.2578), (0.0063, 0.2546), (0.0069, 0.2515), (0.0075, 0.2484), (0.0082, 0.2452), (0.0089, 0.2421), (0.0096, 0.239), (0.0104, 0.2359), (0.0112, 0.2328), (0.012, 0.2298), (0.0128, 0.2267), (0.0137, 0.2236), (0.0146, 0.2206), (0.0155, 0.2176), (0.0165, 0.2145), (0.0175, 0.2115), (0.0185, 0.2085), (0.0195, 0.2055), (0.0206, 0.2025), (0.0217, 0.1996), (0.0228, 0.1966), (0.0239, 0.1936), (0.0251, 0.1907), (0.0263, 0.1878), (0.0275, 0.1849), (0.0288, 0.182), (0.0301, 0.1791), (0.0314, 0.1762), (0.0327, 0.1734), (0.0341, 0.1705), (0.0354, 0.1677), (0.0368, 0.1649), (0.0383, 0.1621), (0.0397, 0.1593), (0.0412, 0.1566), (0.0427, 0.1538), (0.0443, 0.1511), (0.0458, 0.1484), (0.0474, 0.1457), (0.049, 0.143), (0.0507, 0.1404), (0.0523, 0.1377), (0.054, 0.1351), (0.0557, 0.1325), (0.0574, 0.1299), (0.0592, 0.1274), (0.061, 0.1248), (0.0628, 0.1223), (0.0646, 0.1198), (0.0664, 0.1173), (0.0683, 0.1148), (0.0702, 0.1124), (0.0721, 0.1099), (0.0741, 0.1075), (0.076, 0.1052), (0.078, 0.1028), (0.08, 0.1005), (0.082, 0.0981), (0.0841, 0.0958), (0.0861, 0.0936), (0.0882, 0.0913), (0.0903, 0.0891), (0.0924, 0.0869), (0.0946, 0.0847), (0.0968, 0.0825), (0.0989, 0.0804), (0.1011, 0.0783), (0.1034, 0.0762), (0.1056, 0.0742), (0.1079, 0.0721), (0.1101, 0.0701), (0.1124, 0.0681), (0.1148, 0.0662), (0.1171, 0.0642), (0.1194, 0.0623), (0.1218, 0.0604), (0.1242, 0.0586), (0.1266, 0.0567), (0.129, 0.0549), (0.1315, 0.0531), (0.1339, 0.0514), (0.1364, 0.0497), (0.1389, 0.048), (0.1414, 0.0463), (0.1439, 0.0447), (0.1464, 0.043), (0.149, 0.0414), (0.1515, 0.0399), (0.1541, 0.0384), (0.1567, 0.0368), (0.1593, 0.0354), (0.1619, 0.0339), (0.1645, 0.0325), (0.1672, 0.0311), (0.1698, 0.0297), (0.1725, 0.0284), (0.1751, 0.0271), (0.1778, 0.0258), (0.1805, 0.0246), (0.1832, 0.0234), (0.186, 0.0222), (0.1887, 0.021), (0.1914, 0.0199), (0.1942, 0.0188), (0.197, 0.0177), (0.1997, 0.0167), (0.2025, 0.0157), (0.2053, 0.0147), (0.2081, 0.0138), (0.2109, 0.0129), (0.2137, 0.012), (0.2166, 0.0111), (0.2194, 0.0103), (0.2222, 0.0095), (0.2251, 0.0088), (0.2279, 0.008), (0.2308, 0.0073), (0.2337, 0.0067), (0.2365, 0.006), (0.2394, 0.0054), (0.2423, 0.0049), (0.2452, 0.0043), (0.2481, 0.0038), (0.251, 0.0033), (0.2539, 0.0029), (0.2568, 0.0025), (0.2597, 0.0021), (0.2626, 0.0017), (0.2655, 0.0014), (0.2684, 0.0011), (0.2714, 0.0009), (0.2743, 0.0007), (0.2772, 0.0005), (0.2801, 0.0003), (0.2831, 0.0002), (0.286, 0.0001), (0.2889, 0.0), (0.2918, 0.0), (0.2948, 0.0), (0.2977, 0.0), (0.3006, 0.0001), (0.3036, 0.0002), (0.3065, 0.0003), (0.3094, 0.0005), (0.3123, 0.0007), (0.3153, 0.0009), (0.3182, 0.0012), (0.3211, 0.0015), (0.324, 0.0018), (0.3269, 0.0021), (0.3298, 0.0025), (0.3327, 0.0029), (0.3357, 0.0034), (0.3385, 0.0039), (0.3414, 0.0044), (0.3443, 0.0049), (0.3472, 0.0055), (0.3501, 0.0061), (0.353, 0.0067), (0.3558, 0.0074), (0.3587, 0.0081), (0.3615, 0.0088), (0.3644, 0.0096), (0.3672, 0.0104), (0.3701, 0.0112), (0.3729, 0.0121), (0.3757, 0.013), (0.3785, 0.0139), (0.3813, 0.0148), (0.3841, 0.0158), (0.3869, 0.0168), (0.3896, 0.0179), (0.3924, 0.0189), (0.3952, 0.02), (0.3979, 0.0211), (0.4006, 0.0223), (0.4034, 0.0235), (0.4061, 0.0247), (0.4088, 0.026), (0.4115, 0.0272), (0.4141, 0.0286), (0.4168, 0.0299), (0.4194, 0.0313), (0.4221, 0.0326), (0.4247, 0.0341), (0.4273, 0.0355), (0.4299, 0.037), (0.4325, 0.0385), (0.4351, 0.04), (0.4376, 0.0416), (0.4402, 0.0432), (0.4427, 0.0448), (0.4452, 0.0465), (0.4477, 0.0481), (0.4502, 0.0498), (0.4527, 0.0516), (0.4551, 0.0533), (0.4575, 0.0551), (0.46, 0.0569), (0.4624, 0.0588), (0.4647, 0.0606), (0.4671, 0.0625), (0.4695, 0.0644), (0.4718, 0.0664), (0.4741, 0.0683), (0.4764, 0.0703), (0.4787, 0.0723), (0.4809, 0.0744), (0.4832, 0.0764), (0.4854, 0.0785), (0.4876, 0.0806), (0.4898, 0.0828), (0.492, 0.0849), (0.4941, 0.0871), (0.4962, 0.0893), (0.4983, 0.0916), (0.5004, 0.0919), (0.5025, 0.0897), (0.5046, 0.0875), (0.5068, 0.0853), (0.5089, 0.0831), (0.5111, 0.081), (0.5133, 0.0789), (0.5155, 0.0768), (0.5178, 0.0747), (0.52, 0.0727), (0.5223, 0.0706), (0.5246, 0.0687), (0.5269, 0.0667), (0.5292, 0.0647), (0.5316, 0.0628), (0.5339, 0.0609), (0.5363, 0.0591), (0.5387, 0.0572), (0.5411, 0.0554), (0.5436, 0.0536), (0.546, 0.0519), (0.5485, 0.0501), (0.551, 0.0484), (0.5535, 0.0467), (0.556, 0.0451), (0.5585, 0.0435), (0.561, 0.0419), (0.5636, 0.0403), (0.5662, 0.0388), (0.5687, 0.0372), (0.5713, 0.0358), (0.574, 0.0343), (0.5766, 0.0329), (0.5792, 0.0315), (0.5819, 0.0301), (0.5845, 0.0288), (0.5872, 0.0275), (0.5899, 0.0262), (0.5926, 0.0249), (0.5953, 0.0237), (0.598, 0.0225), (0.6007, 0.0213), (0.6035, 0.0202), (0.6062, 0.0191), (0.609, 0.018), (0.6118, 0.017), (0.6145, 0.016), (0.6173, 0.015), (0.6201, 0.014), (0.6229, 0.0131), (0.6257, 0.0122), (0.6286, 0.0114), (0.6314, 0.0105), (0.6342, 0.0097), (0.6371, 0.009), (0.6399, 0.0082), (0.6428, 0.0075), (0.6457, 0.0068), (0.6485, 0.0062), (0.6514, 0.0056), (0.6543, 0.005), (0.6572, 0.0045), (0.6601, 0.0039), (0.663, 0.0035), (0.6659, 0.003), (0.6688, 0.0026), (0.6717, 0.0022), (0.6746, 0.0018), (0.6775, 0.0015), (0.6804, 0.0012), (0.6833, 0.001), (0.6863, 0.0007), (0.6892, 0.0005), (0.6921, 0.0004), (0.695, 0.0002), (0.698, 0.0001), (0.7009, 0.0), (0.7038, 0.0), (0.7068, 0.0), (0.7097, 0.0), (0.7126, 0.0001), (0.7155, 0.0002), (0.7185, 0.0003), (0.7214, 0.0004), (0.7243, 0.0006), (0.7272, 0.0008), (0.7302, 0.0011), (0.7331, 0.0014), (0.736, 0.0017), (0.7389, 0.002), (0.7418, 0.0024), (0.7447, 0.0028), (0.7476, 0.0033), (0.7505, 0.0037), (0.7534, 0.0042), (0.7563, 0.0048), (0.7592, 0.0053), (0.7621, 0.0059), (0.765, 0.0066), (0.7678, 0.0072), (0.7707, 0.0079), (0.7735, 0.0086), (0.7764, 0.0094), (0.7792, 0.0102), (0.7821, 0.011), (0.7849, 0.0118), (0.7877, 0.0127), (0.7905, 0.0136), (0.7933, 0.0146), (0.7961, 0.0155), (0.7989, 0.0165), (0.8017, 0.0176), (0.8044, 0.0186), (0.8072, 0.0197), (0.8099, 0.0208), (0.8127, 0.022), (0.8154, 0.0232), (0.8181, 0.0244), (0.8208, 0.0256), (0.8235, 0.0269), (0.8262, 0.0282), (0.8288, 0.0295), (0.8315, 0.0309), (0.8341, 0.0323), (0.8368, 0.0337), (0.8394, 0.0351), (0.842, 0.0366), (0.8446, 0.0381), (0.8471, 0.0396), (0.8497, 0.0412), (0.8523, 0.0428), (0.8548, 0.0444), (0.8573, 0.046), (0.8598, 0.0477), (0.8623, 0.0494), (0.8648, 0.0511), (0.8672, 0.0529), (0.8697, 0.0546), (0.8721, 0.0564), (0.8745, 0.0583), (0.8769, 0.0601), (0.8792, 0.062), (0.8816, 0.0639), (0.8839, 0.0658), (0.8863, 0.0678), (0.8886, 0.0698), (0.8908, 0.0718), (0.8931, 0.0738), (0.8954, 0.0759), (0.8976, 0.078), (0.8998, 0.0801), (0.902, 0.0822), (0.9041, 0.0843), (0.9063, 0.0865), (0.9084, 0.0887), (0.9105, 0.0909), (0.9126, 0.0932), (0.9147, 0.0955), (0.9167, 0.0978), (0.9188, 0.1001), (0.9208, 0.1024), (0.9227, 0.1048), (0.9247, 0.1071), (0.9267, 0.1095), (0.9286, 0.112), (0.9305, 0.1144), (0.9323, 0.1169), (0.9342, 0.1194), (0.936, 0.1219), (0.9378, 0.1244), (0.9396, 0.1269), (0.9414, 0.1295), (0.9431, 0.1321), (0.9448, 0.1347), (0.9465, 0.1373), (0.9482, 0.1399), (0.9498, 0.1426), (0.9514, 0.1453), (0.953, 0.1479), (0.9546, 0.1507), (0.9561, 0.1534), (0.9576, 0.1561), (0.9591, 0.1589), (0.9606, 0.1617), (0.962, 0.1644), (0.9634, 0.1673), (0.9648, 0.1701), (0.9662, 0.1729), (0.9675, 0.1758), (0.9688, 0.1786), (0.9701, 0.1815), (0.9714, 0.1844), (0.9726, 0.1873), (0.9738, 0.1902), (0.975, 0.1932), (0.9761, 0.1961), (0.9772, 0.1991), (0.9783, 0.202), (0.9794, 0.205), (0.9805, 0.208), (0.9815, 0.211), (0.9825, 0.214), (0.9834, 0.2171), (0.9843, 0.2201), (0.9852, 0.2231), (0.9861, 0.2262), (0.987, 0.2293), (0.9878, 0.2323), (0.9886, 0.2354), (0.9893, 0.2385), (0.9901, 0.2416), (0.9908, 0.2447), (0.9915, 0.2478), (0.9921, 0.251), (0.9927, 0.2541), (0.9933, 0.2572), (0.9939, 0.2604), (0.9944, 0.2635), (0.9949, 0.2667), (0.9954, 0.2698), (0.9959, 0.273), (0.9963, 0.2762), (0.9967, 0.2793), (0.997, 0.2825), (0.9974, 0.2857), (0.9977, 0.2889), (0.9979, 0.2921), (0.9982, 0.2953), (0.9984, 0.2985), (0.9986, 0.3017), (0.9987, 0.3049), (0.9989, 0.3081), (0.999, 0.3113), (0.999, 0.3145), (0.9991, 0.3177), (0.9991, 0.3209), (0.9991, 0.3241), (0.999, 0.3273), (0.9989, 0.3305), (0.9988, 0.3337), (0.9987, 0.3369), (0.9985, 0.3401), (0.9983, 0.3433), (0.9981, 0.3465), (0.9979, 0.3497), (0.9976, 0.3528), (0.9973, 0.356), (0.9969, 0.3592), (0.9966, 0.3624), (0.9962, 0.3656), (0.9957, 0.3687), (0.9953, 0.3719), (0.9948, 0.3751), (0.9943, 0.3782), (0.9937, 0.3814), (0.9932, 0.3845), (0.9926, 0.3876), (0.9919, 0.3908), (0.9913, 0.3939), (0.9906, 0.397), (0.9899, 0.4001), (0.9891, 0.4032), (0.9884, 0.4063), (0.9876, 0.4094), (0.9867, 0.4124), (0.9859, 0.4155), (0.985, 0.4186), (0.9841, 0.4216), (0.9832, 0.4246), (0.9822, 0.4277), (0.9812, 0.4307), (0.9802, 0.4337), (0.9791, 0.4367), (0.978, 0.4396), (0.9769, 0.4426), (0.9758, 0.4456), (0.9747, 0.4485), (0.9735, 0.4514), (0.9723, 0.4544), (0.971, 0.4573), (0.9698, 0.4602), (0.9685, 0.463), (0.9672, 0.4659), (0.9658, 0.4687), (0.9644, 0.4716), (0.963, 0.4744), (0.9616, 0.4772), (0.9602, 0.48), (0.9587, 0.4827), (0.9572, 0.4855), (0.9557, 0.4882), (0.9541, 0.491), (0.9526, 0.4937), (0.951, 0.4963), (0.9494, 0.499), (0.9477, 0.5017), (0.946, 0.5043), (0.9443, 0.5069), (0.9426, 0.5095), (0.9409, 0.5121), (0.9391, 0.5146), (0.9373, 0.5172), (0.9355, 0.5197), (0.9337, 0.5222), (0.9318, 0.5247), (0.93, 0.5271), (0.9281, 0.5296), (0.9261, 0.532), (0.9242, 0.5344), (0.9222, 0.5368), (0.9202, 0.5391), (0.9182, 0.5414), (0.9162, 0.5437), (0.9141, 0.546)]]
    plotter.plot_paths( svg_paths )
