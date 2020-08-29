# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


class UvpLabels:

    FEATURE_NOT_SUPPORTED_MSG = '(Not supported in this edition)'
    FEATURE_NOT_SUPPORTED_ICON = 'ERROR'

    FEATURE_NOT_SUPPORTED_BY_PACKING_MODE_MSG = '(Not supported by the packing mode)'

    PACKING_DEVICE_WARNING="If you don't see your Cuda GPU in the list, make sure you have latest GPU drivers installed"

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

    PIXEL_MARGIN_METHOD_NAME='Pixel Margin Method'
    PIXEL_MARGIN_METHOD_DESC='Select a method the packer will use to determine proper pixel margin'

    PIXEL_MARGIN_METHOD_ADJUSTMENT_TIME_DESC="Determine proper pixel margin by running an algorithm for a time specified by the 'Adjustemt Time' parameter. This method gives exact results in a short time in most cases."
    PIXEL_MARGIN_METHOD_ITERATIVE_DESC="This method guarantees to always determine exact pixel margin, but it requires a number of iterations to be performed and ususally gives slightly worse coverage than the 'Adjustment Time' method. Use the 'Iterative' method only in rare cases when you cannot get good margin results with the 'Adjustemt Time' method, despite setting longer adjustment times. Because the 'Iterative' method gives sightly worse coverage, it is recommended to always combine this option with the 'Heuristic Search' functionality"

    PIXEL_MARGIN_ADJUST_TIME_NAME='Adjustment Time (s)'
    PIXEL_MARGIN_ADJUST_TIME_DESC="Time in seconds the packer will spend on determing proper pixel margin. Time set to 1 second is enough in most cases, increase this parameter only if you don't get an exact result for a specific UV map. This parameter is only used if the pixel margin method is set to 'Adjustment Time'. For more info click the Help button"

    PIXEL_MARGIN_TEX_SIZE_NAME='Texture Size'
    PIXEL_MARGIN_TEX_SIZE_DESC="Texture size in pixels used for pixel margin calculation. If the 'Use Texture Ratio' option is enabled, then this property is ignored and the dimensions of the active texture are used to calculate pixel margin"

    ROT_ENABLE_NAME='Rotation Enable'
    ROT_ENABLE_DESC='Allow the packer to rotate islands in order to achieve better result'

    PREROT_DISABLE_NAME='Pre-Rotation Disable'
    PREROT_DISABLE_DESC='Disable the initial rotatation of islands before generating other orientations. The pre-rotation operation usually optimizes packing, use this option only if you have a good reason'

    NORMALIZE_ISLANDS_NAME='Normalize Islands'
    NORMALIZE_ISLANDS_DESC='Automatically scale selected islands before packing so that the average texel density is the same for every island. WARNING: if lock overlapping is enabled, then normalization takes place AFTER overlapping islands are locked'

    FIXED_SCALE_NAME='Fixed Scale'
    FIXED_SCALE_DESC="Do not scale islands during packing. Packer will return an error if UV islands can't fit into the packing box"

    ROT_STEP_NAME='Rotation Step'
    ROT_STEP_DESC="Rotation step (in degrees) to use when generating island orientations which will be considered during packing."

    ISLAND_ROT_STEP_NAME='Rotation Step Value'
    ISLAND_ROT_STEP_DESC="Rotation step value (in degrees) to be set for the selected islands"

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

    PACK_MODE_GROUPS_TOGETHER_NAME='Groups Together'
    PACK_MODE_GROUPS_TOGETHER_DESC="Group islands using the 'Grouping Method' parameter. Pack all groups into a single tile, islands belonging to the same group will be neighbors after packing. For some UV layouts it is required to use the 'Heuristic Search' option in order to obtain a decent result in this mode"

    PACK_MODE_GROUPS_TO_TILES_NAME='Groups To Tiles'
    PACK_MODE_GROUPS_TO_TILES_DESC="Group islands using the 'Grouping Method' parameter. Pack every group into a separate tile"

    GROUP_METHOD_NAME="Grouping Method"
    GROUP_METHOD_DESC="Grouping method to use"

    GROUP_COMPACTNESS_NAME="Grouping Compactness"
    GROUP_COMPACTNESS_DESC="A value from 0 to 1 specifying how much the packer should prefer solutions providing more compact grouping, when packing groups together. A lower value means the packer will strive less to achieve compact grouping, at the same time it will prioritize achieving better coverage of the overall packing. With a greater value of the parameter, groups will be packed more compactly, but the coverage of the entire solution might be worse. WARNING: use this parameter with care - a small increase of its value might considerably change the result you will get"

    MANUAL_GROUP_NUM_NAME="Group Number"
    MANUAL_GROUP_NUM_DESC="Manual group number to be assigned to the selected islands"

    TILE_COUNT_NAME="Tile Count"
    TILE_COUNT_DESC="Specify the number of tiles which will be used during packing. If set to '0', then the number of tiles is unlimited"

    TILES_IN_ROW_NAME="Tiles In Row"
    TILES_IN_ROW_DESC="When packing to tiles, this parameter determines the number of UDIM tiles in a single tile row"

    LOCK_OVERLAPPING_MODE_NAME='Lock Overlapping'
    LOCK_OVERLAPPING_MODE_DESC='Treat overlapping islands as a single island'

    LOCK_OVERLAPPING_MODE_DISABLED_DESC="Overlapping islands won't be locked"
    LOCK_OVERLAPPING_MODE_ANY_PART_DESC="Two islands will be locked together if only they overlap by any part"
    LOCK_OVERLAPPING_MODE_EXACT_DESC="Two islands will be locked together only if they have the same bounding boxes in the UV space and have identical area"

    PRE_VALIDATE_NAME='Automatic UV Pre-Validation'
    PRE_VALIDATE_DESC='Automatically validate the UV map before packing. If any invalid UV face is found during validation, packing will be aborted and the given UV faces will be selected. WARNING: enabling this option may increase the packing initialization time for UV maps with the huge number of faces, use it with care'

    HEURISTIC_ENABLE_NAME='Enable Heuristic'
    HEURISTIC_ENABLE_DESC="Perform multiple packing iterations in order to find the optimal result."

    HEURISTIC_SEARCH_TIME_NAME='Search Time (s)'
    HEURISTIC_SEARCH_TIME_DESC='Specify a time in seconds for the heuristic search. After timeout is reached the packer will stop and the best result will be applied to the UV map. If the time is set to 0 the packer will perfrom the search continuously, until the user manually applies the result by pressing ESC'

    HEURISTIC_MAX_WAIT_TIME_NAME='Max Wait Time (s)'
    HEURISTIC_MAX_WAIT_TIME_DESC="Maximal time the packer will wait for a better result. If the heuristic algorithm is not able to find a tighter packing during that time, the operation will be automatically finished and the best result found so far will be applied to the UV map. If set to 0, then the functionality will be disabled"

    ADVANCED_HEURISTIC_NAME='Advanced Heuristic'
    ADVANCED_HEURISTIC_DESC="Use an advanced method during a heuristic search. With this option enabled add-on will examine a broader set of solutions when searching for the optimal one. This method is most useful when packing a limited number of islands - in such case it allows to find a better solution than if using the simple method. Enabling this option is not recommended when packing a UV map containing a greater number of islands"

    SIMILARITY_THRESHOLD_NAME='Similarity Threshold'
    SIMILARITY_THRESHOLD_DESC="A greater value of this parameter means islands will be more likely recognized as a similar in shape. A lower value means more accurate distinction. For more info regarding similarity detection click the help button"
    
    MULTI_DEVICE_PACK_NAME='Use All Devices'
    MULTI_DEVICE_PACK_DESC="If this option is enabled, the add-on will use all packing devices simultaneously whenever possible."

    FULLY_INSIDE_NAME='Only Islands Fully Inside'
    FULLY_INSIDE_DESC="Process only islands which are fully inside the packing box"

    MOVE_ISLANDS_NAME='Move Box With Islands'
    MOVE_ISLANDS_DESC="Move the packing box together with selected islands inside"

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

    CUDA_MACOS_CONFIRM_MSG = 'WARNING: Cuda support on MacOS is experimental. Click OK to continue'
    GROUPS_TOGETHER_CONFIRM_MSG = 'WARNING: packing groups together requires the heuristic search to produce an optimal result - it is strongy recommended to enable it before continuing. Press OK to continue, click outside the pop-up to cancel the operation'

    SEED_NAME='Seed'
    TEST_PARAM_NAME='Test Parameter'
    WRITE_TO_FILE_NAME='Write UV Data To File'
    SIMPLIFY_DISABLE_NAME='Simplify Disable'
    WAIT_FOR_DEBUGGER_NAME='Wait For Debugger'

    HELP_BASEURL = "https://glukoz.dev/uvp/blender/help/"
