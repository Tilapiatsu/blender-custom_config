
class UvpLabels:

    FEATURE_NOT_SUPPORTED_MSG = '(Not supported in this edition)'
    FEATURE_NOT_SUPPORTED_ICON = 'ERROR'

    # Property labels

    THREAD_COUNT_NAME='Thread Count'
    THREAD_COUNT_DESC="Number of threads that will be used by the packer"

    OVERLAP_CHECK_NAME='Automatic Overlap Check'
    OVERLAP_CHECK_DESC='Automatically check for overlapping islands after packing is done'

    AREA_MEASURE_NAME='Automatic Area Measurement'
    AREA_MEASURE_DESC='Automatically measure islands area after packing is done'

    PRECISION_NAME='Precision'
    PRECISION_DESC='Number describing how exact the algorithm will be when searching for island placement. Too low value may cause islands to overlap'

    MARGIN_NAME='Margin'
    MARGIN_DESC='Margin to apply during packing'

    PIXEL_MARGIN_NAME='Pixel Margin'
    PIXEL_MARGIN_DESC="Margin in pixels of the active texture the resulting UV map should have. If this parameter is set to a value greater than 0, then the usual 'Margin' option will be ignored and the packer will try to determine the correct pixel margin. The pixel margin functionality needs the 'Heuristic Search' option enabled in order to work properly in a general case. For more info click the Help button"

    PIXEL_PADDING_NAME='Pixel Padding'
    PIXEL_PADDING_DESC="Distance in pixels between UV islands and the packing box border. This option is disabled and ignored if set to '0' - in such case the distance will be determined by the island margin"

    PIXEL_MARGIN_TEX_SIZE_NAME='Texture Size'
    PIXEL_MARGIN_TEX_SIZE_DESC="Texture size in pixels used for pixel margin calculation. If the 'Use Texture Ratio' option is enabled, then this property is ignored and the dimensions of the active texture are used to calculate pixel margin"

    ROT_ENABLE_NAME='Rotation Enable'
    ROT_ENABLE_DESC='Allow the packer to rotate islands in order to achieve better result'

    PREROT_DISABLE_NAME='Pre-Rotation Disable'
    PREROT_DISABLE_DESC='Disable the initial rotatation of islands before generating other orientations. The pre-rotation operation usually optimizes packing, use this option only if you have a good reason'

    POSTSCALE_DISABLE_NAME='Post-Scaling Disable'
    POSTSCALE_DISABLE_DESC='Do not scale islands after packing in order to fit them into unit UV square. Enabling this option is not recommended in most cases'

    ROT_STEP_NAME='Rotation Step'
    ROT_STEP_DESC="Rotation step in degrees to apply during packing"

    ISLAND_ROT_STEP_NAME='Island Rotation Step Value'
    ISLAND_ROT_STEP_DESC="Rotation step value (in degress) to be set for the selected islands"

    ISLAND_ROT_STEP_ENABLE_NAME='Enable Island Rotation Step'
    ISLAND_ROT_STEP_ENABLE_DESC="Enable per-island rotation step"

    PACKING_DEPTH_NAME='Packing Depth'

    TEX_RATIO_NAME='Use Texture Ratio'
    TEX_RATIO_DESC='Take into consideration the ratio of the active texture dimensions during packing'

    PACK_TO_OTHERS_NAME='Pack To Others'
    PACK_TO_OTHERS_DESC='Add selected islands into those already packed in the unit UV square (no scaling will be applied)'

    PACK_MODE_NAME='Packing Mode'
    PACK_MODE_DESC="Select how the packer should process the UV map"

    PACK_MODE_SINGLE_TILE_NAME='Single Tile'
    PACK_MODE_SINGLE_TILE_DESC='Standard packing to a single tile'

    PACK_MODE_TILES_FIXED_SCALE_NAME='Tiles (Fixed Scale)'
    PACK_MODE_TILES_FIXED_SCALE_DESC='Pack islands to many tiles without scaling them. If there is no room to pack an island in the current tile, it will be packed into the next tile. Packing will fail if the UV map contains an island larger than a single tile'

    PACK_MODE_GROUPS_TOGETHER_NAME='Groups Together (Experimental)'
    PACK_MODE_GROUPS_TOGETHER_DESC="Group islands using the 'Grouping Method' parameter. Pack all groups into a single tile, islands belonging to the same group will be neighbors after packing. For some UV layouts it is required to use the 'Heuristic Search' option in order to obtain a decent result in this mode"

    PACK_MODE_GROUPS_TO_TILES_NAME='Groups To Tiles'
    PACK_MODE_GROUPS_TO_TILES_DESC="Group islands using the 'Grouping Method' parameter. Pack every group into a separate tile"

    GROUP_METHOD_NAME="Grouping Method"
    GROUP_METHOD_DESC="Grouping method to use"

    TILES_IN_ROW_NAME="Tiles In Row"
    TILES_IN_ROW_DESC="Number of UDIM tiles in a single row. 10 is a common standard"

    LOCK_OVERLAPPING_NAME='Lock Overlapping'
    LOCK_OVERLAPPING_DESC='Treat overlapping islands as a single island'

    PRE_VALIDATE_NAME='Automatic UV Pre-Validation'
    PRE_VALIDATE_DESC='Automatically validate the UV map before packing. If any invalid UV face is found during validation, packing will be aborted and the given UV faces will be selected. WARNING: enabling this option may increase the packing initialization time for UV maps with the huge number of faces, use it with care'

    HEURISTIC_ENABLE_NAME='Enable Heuristic'
    HEURISTIC_ENABLE_DESC="Perform multiple packing iterations in order to find the optimal result. This feature is most useful when a single packing pass doesn't take much time (a few seconds). Use it with a limited number of islands and with limited island orientations considered ('Rotation Step' == 90). Before doing a long search it is recommended to run a single packing pass in order to determine whether overlaps are not likely to happen for given 'Precision' and 'Margin' parameters"

    HEURISTIC_SEACH_TIME_NAME='Heuristic Search Time (s)'
    HEURISTIC_SEACH_TIME_DESC='Specify a time in seconds for the heuristic search. After timeout is reached the packer will stop and the best result will be applied to the UV map. If the time is set to 0 the packer will perfrom the search continuously, until the user manually applies the result by pressing ESC'

    PIXEL_MARGIN_ADJUST_TIME_NAME='Adjustment Time (s)'
    PIXEL_MARGIN_ADJUST_TIME_DESC="The time in seconds packer will spend on determing the proper pixel margin before actual packing begins. This parameter is only used if the 'Pixel Margin' parameter is greater than 0. For more info click the Help button"

    ADVANCED_HEURISTIC_NAME='Advanced Heuristic'
    ADVANCED_HEURISTIC_DESC="Use an advanced method during a heuristic search. With this option enabled add-on will examine a broader set of solutions when searching for the optimal one. This method is most useful when packing a limited number of islands, preferably with a greater number of orientations considered - in such case it allows to find a better solution than if using the simple method. Enabling this option is not recommended when packing a UV map containing a greater number of islands"

    SIMILARITY_THRESHOLD_NAME='Similarity Threshold'
    SIMILARITY_THRESHOLD_DESC="A greater value of this parameter means islands will be more likely recognized as a similar in shape. For more info regarding similarity detection click the help button"
    
    MULTI_DEVICE_PACK_NAME='Use All Devices'
    MULTI_DEVICE_PACK_DESC="If this option is enabled, the add-on will use all packing devices simultaneously whenever possible. Simultaneous packing mode will be used in the following situations: heuristic search is enabled or the packing mode is set to '{}'".format(PACK_MODE_GROUPS_TO_TILES_NAME)

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

    # Non-square packing help

    NONSQUARE_PACKING_HELP_P1 = "In order to pack islands to a non-square texture follow the procedure:"
    NONSQUARE_PACKING_HELP_P2 = "Note that now you can use the 'Pack To Others' option also when packing to a non-square texture. But rembember that all new islands you want to add to the packing must be adjusted to the given non-square texture first (for example by using the 'Adjust Islands To Texture' operation)."
    NONSQUARE_PACKING_HELP_P3 = "You can also undo the adjustment operation. In order to do that select given islands and click 'Undo Islands Adjustment' button. After the action is done islands will be deformed again when dispalyed at the non-square texture. When you close the texture you will see that the islands will have proper proportions at the unit UV square. Note that for the undo operation to work properly the texture used at the time of undoing must have the same ratio as the texture islands were orginally adjusted to."

    NONSQUARE_PACKING_HELP_STEPS = [
        "unwrap your islands in the usual manner so they are not deformed when displayed at the unit UV square",
        "open or create a non-square texture in the UV editor. You will notice that islands will be deformed now",
        "next step is adjusting islands to the texture i.e. applying non-uniform scaling so they have correct proportions with the given texture. You can do it manually, you can also use the addon to perform scaling automatically. In order to do that select all islands you want to adjust and click 'Adjust Islands To Texture' button. You will see that islands will have correct proportions after action is done (they will be no longer deformed with the given non-square texture). Note that this operation must be performed only once for the given islands",
        "enable the 'Use Texture Ratio' option",
        "from now you can run the packing operation normally. You can pack islands multiple times and their proportions will always be correct with the given non-square texture"
    ]

    SIMILARITY_DETECTION_HELP_P1 = "Accuracy of similar islands detection depends on the three factors:"

    SIMILARITY_DETECTION_HELP_LIST = [
        "'Similarity Threshold' parameter: a greater value of this parameter means islands will be more likely recognized as a similar in shape. '0.5' is a good threshold value to start with",
        "'Precision' paramter: more precision means better accuracy in looking for similar islands. Precision set to 200 should be sufficient in most cases. This value should be increased in the first place if the similarity detection returns incorrect results (especially when dealing with really small islands)",
        "'Rotation Step' paramter: the lower rotation step value the better accuracy of the operation. Rotation step set to 90 should be sufficient in most cases though",
    ]

    INVALID_TOPOLOGY_HELP_P1 = "The add-on is able to process almost all kind of UV topology, even if it is really bad (e.g. faces with self-intersecting edges, many doubled vertices etc). In very rare cases however, due to floating point precision errors, topology of some UV islands cannot be analysed properly. In such situtation the add-on will return 'Invalid Topology' error and select all problematic UV islands. You have two options to solve this kind of problem:"

    INVALID_TOPOLOGY_HELP_LIST = [
        "fix the topology of the islands (unwrap the islands properly so they do not have doubled vertices, self-intersecting edges). It is the recommended way",
        "try to apply a simple transformation to the islands and check whether the 'Invalid Topology' error disappers. This method works because topology issues are caused by floating point precision errors. A transformation will change UV coordinates and the outcome of floating point operations may be different. A simple transformation can be: rotating by 90 degress, scaling by 1.01, moving the islands to a different place"
    ]

    PIXEL_MARGIN_HELP_P1 = "The 'Pixel Margin' parameter allows you to determine the margin of the resulting UV map in pixels of the active texture. In order to use this option set the 'Pixel Margin' parameter to a value greater than zero. In such situation the standard 'Margin' option will be ignored and packer will try to determine the correct pixel margin. In order to make sure that the packed UV map will have exact pixel margin one should also set a proper value of the 'Adjustment Time' parameter. During that time packer will be determining what margin should be applied to the given UV map before packing, so that the resulting margin after packing is equal to the requested number of pixels. Such adjustment is required because in a general case the UV islands are scaled after packing is done (so they fit the unit UV square), so is the margin applied to the islands before packing. After the adjustment phase is done the actual packing process will begin."
    
    PIXEL_MARGIN_HELP_P2 = "A rule of thumb is that the longer the adjustment time the more accurate the resulting pixel margin will be. In practice the adjustment time set to one second should be enough for a usual UV map. Set the adjustment time to greater values only if the resulting pixel margin is not accurate enough for the given UV map."

    PIXEL_MARGIN_HELP_P3 = "Note that in some cases the pixel margin adjustment phase is not needed at all. It is the case when UV scaling is not performed after packing. Scaling is skipped in the following situations: 1. the 'Pack To Others' option is enabled. 2. 'Tiles (Fixed Scale)' packing mode is selected. 3. scaling is explicitly disabled by checking the 'Post-Scale Disable' option. In such situation the 'Adjustment Time' option will be ignored."

    ISLAND_ROT_STEP_HELP_P1 = "The Island Rotation Step functionality allows you to define rotation step separately for every island. In order to use it check the 'Enable Island Rotation Step' option in the 'Island Rotation Step' subpanel. By default all islands will have a special 'G' rotation step value assigned to them - it means that they will use the global 'Rotation Step' setting from the 'Basic Options' subpanel."

    ISLAND_ROT_STEP_HELP_P2 = "In order to pack with the rotation step value on per-island level:"
    
    ISLAND_ROT_STEP_HELP_LIST = [
        "select islands for which you want to set a new rotation step value",
        "choose a new value to be set using the 'Island Rotation Step Value' parameter",
        "click the 'Set Island Rotation Step' button. You will see that the new rotation step value will be shown near the selected islands in the UV editor as a confirmation that the operation was successful",
        "press any button in order to hide rotation step values in the UV editor and continue working with Blender",
        "repeat above steps for all islands for which you want to assing a specific rotation step value",
        "finally press the 'Pack' button - islands will use rotation step defined on the island level."
    ]

    ISLAND_ROT_STEP_HELP_P3 = "Note that setting rotation step value to '0' means that rotations will be disabled for given islands i.e. only one orientation will be considered for every one of them (the add-on may still apply so-called pre-rotation before packing, so if you want the islands not to be rotated at all you should also check the 'Pre-Rotation Disable' option in the 'Basic Options' subpanel). If you would like specific islands to use the global rotation step value again (the default behavior), select these islands and press the 'Reset Island Rotation Step' button"

    ISLAND_ROT_STEP_HELP_P4 = "If you want to disable the Island Rotation Step functionality simply uncheck the 'Enable Island Rotation Step' option - all islands will start using the global Rotatin Step value again. Keep in mind that disabling the functionality does not cause per-island rotation step values to be forgotten - they will stay unchanged and will be used again as soon as you enable the island Rotation Step functionality. They will be maintained even after the blend file is closed assuming that you saved the file after setting values."

    ISLAND_ROT_STEP_HELP_P5 = "WARNING: note that per-island parameters are in fact implemented by the add-on on the UV face level (due to Blender API limitations). It means that you could possibly assign a separate rotation step value for every UV face in your map. In order to keep rotation step values consistent the add-on performs a check before packing and raises error if it detects that two UV faces belonging to the same island have different rotation step values assigned. The problematic islands will be selected by the add-on so you could easily assign consistent values to them. Also keep in mind that per-island rotation step values are internally saved using a specific vertex color channel. The channel has a hardcoded name starting with the '__uvp2' prefix - make sure you do not modify this channel manually, otherwise the functionality will not work properly. If you think the channel values might be malformed you can reset the rotation step values by simply removing the channel."
    

    UVP_SETUP_HELP_P1 = "In order to use the packing features of the add-on you need to manually provide a path to the UVP engine in the correct version (if you didn't purchase the UVP engine you can always use the engine demo version for free). Follow the steps:"

    UVP_SETUP_HELP_LIST = [
        "Download an engine package from the product page (the name of the package follows a pattern: uvp-{EDITION}-{VERSION}.zip). Make sure you use the correct engine version. You can use any engine edition, but it will determine a set of packing features which will be available.",

        "Extract the engine package at any location convenient for you.",

        "At the top of the UVPackmaster add-on interface in Blender press the 'Select UVP Engine' button (a small button next to the engine path field). A file browser will pop up.",

        "In the file browser navigate to the path where you extraced the engine package and localize a file named 'release-{VERSION}.uvpini' - select the file in the browser.",

        "The engine will be automatically initialized and you can immediatelly start using UVP packing features in Blender.",

        "In order to make sure the new engine path will be preserved after Blender is closed go to the Blender Preferences window and click 'Save Preferences'.",
 ]
