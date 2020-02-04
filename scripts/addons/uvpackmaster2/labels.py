
class UvpLabels:

    FEATURE_NOT_SUPPORTED_MSG = '(Not supported in this edition)'
    FEATURE_NOT_SUPPORTED_ICON = 'ERROR'

    FEATURE_NOT_SUPPORTED_BY_PACKING_MODE_MSG = '(Not supported by the packing mode)'

    # Property labels

    THREAD_COUNT_NAME='Thread Count'
    THREAD_COUNT_DESC="Choose the maximal number of CPU cores which will be used by the plugin. By default this parameter is set to the number of cores in the system"

    PRECISION_NAME='Precision'
    PRECISION_DESC='Number describing how exact the algorithm will be when searching for island placement. Too low value may cause islands to overlap'

    MARGIN_NAME='Margin'
    MARGIN_DESC='Margin to apply during packing'

    PIXEL_MARGIN_NAME='Pixel Margin'
    PIXEL_MARGIN_DESC="Margin in pixels the packed UV islands should have. If this parameter is set to a value greater than 0, then the usual 'Margin' option will be ignored and the packer will determine the correct pixel margin"

    PIXEL_PADDING_NAME='Pixel Padding'
    PIXEL_PADDING_DESC="Distance in pixels between UV islands and the packing box border. This option is disabled and ignored if set to '0' - in such case the distance will be determined by the island margin"

    PIXEL_MARGIN_TEX_SIZE_NAME='Texture Size'
    PIXEL_MARGIN_TEX_SIZE_DESC="Texture size in pixels used for pixel margin calculation. If the 'Use Texture Ratio' option is enabled, then this property is ignored and the dimensions of the active texture are used to calculate pixel margin"

    ROT_ENABLE_NAME='Rotation Enable'
    ROT_ENABLE_DESC='Allow the packer to rotate islands in order to achieve better result'

    PREROT_DISABLE_NAME='Pre-Rotation Disable'
    PREROT_DISABLE_DESC='Disable the initial rotatation of islands before generating other orientations. The pre-rotation operation usually optimizes packing, use this option only if you have a good reason'

    FIXED_SCALE_NAME='Fixed Scale'
    FIXED_SCALE_DESC="Do not scale islands during packing. Packer will return an error if UV islands can't fit into the packing box"

    ROT_STEP_NAME='Rotation Step'
    ROT_STEP_DESC="Rotation step (in degrees) to use when generating island orientations which will be considered during packing."

    ISLAND_ROT_STEP_NAME='Rotation Step Value'
    ISLAND_ROT_STEP_DESC="Rotation step value (in degress) to be set for the selected islands"

    ISLAND_ROT_STEP_ENABLE_NAME='Enable Island Rotation Step'
    ISLAND_ROT_STEP_ENABLE_DESC="Enable per-island rotation step"

    PACKING_DEPTH_NAME='Packing Depth'

    TEX_RATIO_NAME='Use Texture Ratio'
    TEX_RATIO_DESC='Take into consideration the ratio of the active texture dimensions during packing'

    PACK_TO_OTHERS_NAME='Pack To Others'
    PACK_TO_OTHERS_DESC='Pack selected islands so they do not overlap with unselected islands. Using this mode you can add new islands into a packed UV map'

    PACK_MODE_NAME='Packing Mode'
    PACK_MODE_DESC="Determines how the packer processes the UV map"

    PACK_MODE_SINGLE_TILE_NAME='Single Tile'
    PACK_MODE_SINGLE_TILE_DESC='Standard packing to a single tile'

    PACK_MODE_TILES_NAME='Tiles'
    PACK_MODE_TILES_DESC='Pack islands to tiles'

    PACK_MODE_GROUPS_TOGETHER_NAME='Groups Together (Experimental)'
    PACK_MODE_GROUPS_TOGETHER_DESC="Group islands using the 'Grouping Method' parameter. Pack all groups into a single tile, islands belonging to the same group will be neighbors after packing. For some UV layouts it is required to use the 'Heuristic Search' option in order to obtain a decent result in this mode"

    PACK_MODE_GROUPS_TO_TILES_NAME='Groups To Tiles'
    PACK_MODE_GROUPS_TO_TILES_DESC="Group islands using the 'Grouping Method' parameter. Pack every group into a separate tile"

    GROUP_METHOD_NAME="Grouping Method"
    GROUP_METHOD_DESC="Grouping method to use"

    MANUAL_GROUP_NUM_NAME="Group Number"
    MANUAL_GROUP_NUM_DESC="Manual group number to be assigned to the selected islands"

    TILE_COUNT_NAME="Tile Count"
    TILE_COUNT_DESC="Specify the number of tiles which will be used during packing. If set to '0', then the number of tiles is unlimited"

    TILES_IN_ROW_NAME="Tiles In Row"
    TILES_IN_ROW_DESC="When packing to tiles, this parameter determines the number of UDIM tiles in a single tile row"

    LOCK_OVERLAPPING_NAME='Lock Overlapping'
    LOCK_OVERLAPPING_DESC='Treat overlapping islands as a single island'

    PRE_VALIDATE_NAME='Automatic UV Pre-Validation'
    PRE_VALIDATE_DESC='Automatically validate the UV map before packing. If any invalid UV face is found during validation, packing will be aborted and the given UV faces will be selected. WARNING: enabling this option may increase the packing initialization time for UV maps with the huge number of faces, use it with care'

    HEURISTIC_ENABLE_NAME='Enable Heuristic'
    HEURISTIC_ENABLE_DESC="Perform multiple packing iterations in order to find the optimal result."

    HEURISTIC_SEACH_TIME_NAME='Heuristic Search Time (s)'
    HEURISTIC_SEACH_TIME_DESC='Specify a time in seconds for the heuristic search. After timeout is reached the packer will stop and the best result will be applied to the UV map. If the time is set to 0 the packer will perfrom the search continuously, until the user manually applies the result by pressing ESC'

    PIXEL_MARGIN_ADJUST_TIME_NAME='Adjustment Time (s)'
    PIXEL_MARGIN_ADJUST_TIME_DESC="The time in seconds packer will spend on determing the proper pixel margin before actual packing begins. This parameter is only used if the 'Pixel Margin' parameter is greater than 0. For more info click the Help button"

    ADVANCED_HEURISTIC_NAME='Advanced Heuristic'
    ADVANCED_HEURISTIC_DESC="Use an advanced method during a heuristic search. With this option enabled add-on will examine a broader set of solutions when searching for the optimal one. This method is most useful when packing a limited number of islands, preferably with a greater number of orientations considered - in such case it allows to find a better solution than if using the simple method. Enabling this option is not recommended when packing a UV map containing a greater number of islands"

    SIMILARITY_THRESHOLD_NAME='Similarity Threshold'
    SIMILARITY_THRESHOLD_DESC="A greater value of this parameter means islands will be more likely recognized as a similar in shape. For more info regarding similarity detection click the help button"
    
    MULTI_DEVICE_PACK_NAME='Use All Devices'
    MULTI_DEVICE_PACK_DESC="If this option is enabled, the add-on will use all packing devices simultaneously whenever possible."

    TARGET_BOX_TILE_X_NAME='Tile (X)'
    TARGET_BOX_TILE_X_DESC='X coordinate of a tile to be set'

    TARGET_BOX_TILE_Y_NAME='Tile (Y)'
    TARGET_BOX_TILE_Y_DESC='Y coordinate of a tile to be set'

    TARGET_BOX_P1_X_NAME='Packing Box P1 (X)'
    TARGET_BOX_P1_X_DESC='X coordinate of the box first corner'

    TARGET_BOX_P1_Y_NAME='Packing Box P1 (Y)'
    TARGET_BOX_P1_Y_DESC='Y coordinate of the box first corner'

    TARGET_BOX_P2_X_NAME='Packing Box P2 (X)'
    TARGET_BOX_P2_X_DESC='X coordinate of the box second corner'

    TARGET_BOX_P2_Y_NAME='Packing Box P2 (Y)'
    TARGET_BOX_P2_Y_DESC='Y coordinate of the box second corner'

    SEED_NAME='Seed'
    TEST_PARAM_NAME='Test Parameter'
    WRITE_TO_FILE_NAME='Write UV Data To File'
    SIMPLIFY_DISABLE_NAME='Simplify Disable'
    WAIT_FOR_DEBUGGER_NAME='Wait For Debugger'

    HELP_BASEURL = "https://glukoz.dev/uvp/blender/help/"
