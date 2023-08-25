class Constants :
    # note that sampling distance is not in actual board millimeters,
    # but in the space of the original SVG
    # For now we do not support scaling the svg before sampling
    # so you just have to fiddle with this and make sure the quality check passes well enough later
    SAMPLING_DISTANCE = 5
    QUALITY_THRESHOLD_DISTANCE_VALUE = 2 # this is in actual board/canvas millimeters

    # Motor settings for power control
    POWER_MAX_PERCENTAGE = 1.0  # use only XX% of available motor power
    POWER_PER_DEGREE_PER_SECOND = 1 / 9.3  # factor to convert from desired deg/s to power that needs to be applied
    MAX_DEG_PER_S = 100 / POWER_PER_DEGREE_PER_SECOND * POWER_MAX_PERCENTAGE

    # Motor settings for positioning
    MM_PER_DEGREE = 3760 / 137816
    POINT_REACHED_ERROR_ACCEPTANCE_MM = 1
    POINT_REACHED_ERROR_ACCEPTANCE_DEGREES = POINT_REACHED_ERROR_ACCEPTANCE_MM / abs( MM_PER_DEGREE )

    # define our coordinate spaces
    # The board is a panel of wood which our anchors are nailed into
    # The canvas is a piece of paper taped to the board
    # By setting a padding we modify the drawable space on the canvas
    # Note that rope lengths and therefore motor degrees always relate to the anchors
    # and should not be confused with board space
    BOARD_SIZE_MM = ( 900, 1250 )
    LEFT_ANCHOR_OFFSET_TO_BOARD_MM = ( 45, 33 )
    RIGHT_ANCHOR_OFFSET_TO_BOARD_MM = ( 865, 33 )
    CANVAS_SIZE_MM = ( 210 * 3, 297 * 2 )#( 210, 297 )
    CANVAS_OFFSET_TO_BOARD_MM = ( 135, 337 )#( 345, 335 )
    CANVAS_PADDING_MM = 20 # will be applie don all sides so *2 in any dimension

    # While we can compute for every point in "canvas-space" target degrees for our motors,
    # it can still be the case that the inner state of the motors is not completely calibrated to the same space
    # By measuring what the motor state is at the beginning of our program,
    # and relating that to the measured position,
    # we can calibrate the motor's internal values.
    # We will measure a designated point on the lego robot itself, because that's easier to do every time.
    # We have measured the offset of the pen with respect to that specific point, once before.
    INITIAL_POSITION_MEASURE_POINT_RELATIVE_TO_BOARD_X_MM = 450 # <- center top of middle A4
    INITIAL_POSITION_MEASURE_POINT_RELATIVE_TO_BOARD_Y_MM = 335 # <- center top of middle A4
    PEN_POSITION_RELATIVE_TO_MEASURE_POINT_X_MM = 0  # mm
    PEN_POSITION_RELATIVE_TO_MEASURE_POINT_Y_MM = 22  # mm

    MAGIC_MOTOR_MODE = [ (1, 0), (2, 2), (3, 1), (0, 0) ]


