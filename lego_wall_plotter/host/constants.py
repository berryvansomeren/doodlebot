

class Constants:
    """
    These constants are used for drawing previews,
    But ROPE_LENGTH_PER_ONE_MAX_POWER_SECOND_MM is absolutely crucial for computing correct motor instructions
    """

    # define our coordinate spaces
    # The board is a panel of wood which our anchors are nailed into
    # The canvas is a piece of paper taped to the board
    # By setting a padding we modify the drawable space
    # Note that rope lengths and therefore motor degrees always relative to the anchors
    # while PlotPacks and its components are always within "drawable-space".
    # For conversions, we often work via "board-space" as the global space
    BOARD_SIZE_MM = ( 900, 1250 )
    LEFT_ANCHOR_OFFSET_TO_BOARD_MM = ( 45, 33 )
    RIGHT_ANCHOR_OFFSET_TO_BOARD_MM = ( 865, 33 )
    CANVAS_SIZE_MM = ( 210, 297 )
    CANVAS_OFFSET_TO_BOARD_MM = (345, 335)
    CANVAS_PADDING_MM = 2 * 20

    MM_PER_DEGREE = 3760 / 137816

    # While we can compute for every point in "canvas-space" target degrees for our motors,
    # it can still be the case that the inner state of the motors is not completely calibrated to the same space
    # By measuring what the motor state is at the beginning of our program,
    # and relating that to the measured position,
    # we can calibrate the motor's internal values.
    # We will measure a designated point on the lego robot itself, because that's easier to do every time.
    # We have measured the offset of the pen with respect to that specific point, once before.
    INITIAL_POSITION_MEASURE_POINT_RELATIVE_TO_BOARD_X_MM = 460
    INITIAL_POSITION_MEASURE_POINT_RELATIVE_TO_BOARD_Y_MM = 557
    PEN_POSITION_RELATIVE_TO_MEASURE_POINT_X_MM = 0 # mm
    PEN_POSITION_RELATIVE_TO_MEASURE_POINT_Y_MM = 22 # mm


