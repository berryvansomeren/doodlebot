class Constants:
    """
    These constants are used for drawing previews,
    But ROPE_LENGTH_PER_ONE_MAX_POWER_SECOND_MM is absolutely crucial for computing correct motor instructions
    """

    # Canvas
    BOARD_SIZE = ( 900, 1250 )
    LEFT_ANCHOR_OFFSET = ( 45, 33 )
    RIGHT_ANCHOR_OFFSET = ( 865, 33 )
    CANVAS_SIZE_MM = ( 210, 297 )
    CANVAS_OFFSET_MM = ( 345, 335 )
    PADDING_MM = 5 * 10

    # How motor speed affects rope consumption
    # this value is how much mm of rope is consumed by running a motor at 100% speed for one second
    ROPE_LENGTH_PER_ONE_MAX_POWER_SECOND_MM = 17

    INITIAL_POSITION_MEASURE_POINT_RELATIVE_TO_BOARD_X_MM = 460
    INITIAL_POSITION_MEASURE_POINT_RELATIVE_TO_BOARD_Y_MM = 557

    PEN_POSITION_RELATIVE_TO_MEASURE_POINT_X_MM = 0 # mm
    PEN_POSITION_RELATIVE_TO_MEASURE_POINT_Y_MM = 22 # mm


def get_initial_position() -> tuple[float, float]:
    return (
        Constants.INITIAL_POSITION_MEASURE_POINT_RELATIVE_TO_BOARD_X_MM + Constants.PEN_POSITION_RELATIVE_TO_MEASURE_POINT_X_MM,
        Constants.INITIAL_POSITION_MEASURE_POINT_RELATIVE_TO_BOARD_Y_MM + Constants.PEN_POSITION_RELATIVE_TO_MEASURE_POINT_Y_MM,
    )