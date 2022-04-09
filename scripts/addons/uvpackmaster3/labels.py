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


class Labels:

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

    PIXEL_MARGIN_ENABLE_NAME='Enable Pixel Margin '
    PIXEL_MARGIN_ENABLE_DESC="Enable the pixel margin functionality. If this parameter is enabled, then the usual 'Margin' option will be ignored and the packer will determine the exact pixel margin"

    PIXEL_MARGIN_NAME='Pixel Margin'
    PIXEL_MARGIN_DESC="Margin in pixels to apply during packing"

    PIXEL_PADDING_NAME='Pixel Padding'
    PIXEL_PADDING_DESC="Distance in pixels between UV islands and the UV target box border. This option is disabled and ignored if set to '0' - in such case the distance will be determined by the island margin"

    EXTRA_PIXEL_MARGIN_TO_OTHERS_NAME='Extra Margin To Others'
    EXTRA_PIXEL_MARGIN_TO_OTHERS_DESC="Specifies an additional pixel margin between islands being packed and the other islands (unselected islands when using the 'Pack To Others' mode). In result the final margin between these islands will be calculated using the formula: 'Pixel Margin' + 'Extra Margin To Others'. When using the 'Groups To Tiles' mode and packing two groups into the same UV space, the islands from the other group are also treated as 'Others'. It means that the 'Extra Margin To Others' parameter will also be taken into account when calculating the margin between islands belonging to different groups."

    PIXEL_MARGIN_ADJUST_TIME_NAME='Adjustment Time (s)'
    PIXEL_MARGIN_ADJUST_TIME_DESC="Time in seconds the packer will spend on determing proper pixel margin. Time set to 1 second is enough in most cases, increase this parameter only if you don't get an exact result for a specific UV map. This parameter is only used if the pixel margin method is set to 'Adjustment Time'. For more info click the Help button"

    PIXEL_MARGIN_TEX_SIZE_NAME='Texture Size'
    PIXEL_MARGIN_TEX_SIZE_DESC="Texture size in pixels used for pixel margin calculation. If the 'Use Texture Ratio' option is enabled, then this property is ignored and the dimensions of the active texture are used to calculate pixel margin"

    ROTATION_ENABLE_NAME='Rotation Enable'
    ROTATION_ENABLE_DESC='Allow the packer to rotate islands in order to achieve better result'

    PRE_ROTATION_DISABLE_NAME='Pre-Rotation Disable'
    PRE_ROTATION_DISABLE_DESC='Disable the initial rotatation of islands before generating other orientations. The pre-rotation operation usually optimizes packing, use this option only if you have a good reason'

    NORMALIZE_ISLANDS_NAME='Normalize Islands'
    NORMALIZE_ISLANDS_DESC='Automatically scale selected islands before packing so that the average texel density is the same for every island. WARNING: if lock overlapping is enabled, then normalization takes place AFTER overlapping islands are locked'

    FIXED_SCALE_NAME='Fixed Scale'
    FIXED_SCALE_DESC="Do not scale islands during packing. Packer will return an error if UV islands can't fit into the UV target box"

    FIXED_SCALE_STRATEGY_NAME='Fixed Scale Strategy'
    FIXED_SCALE_STRATEGY_DESC="Determines how islands are packed when 'Fixed Scale' is on (no scaling is applied to islands)"

    ROTATION_STEP_NAME='Rotation Step'
    ROTATION_STEP_DESC="Rotation step (in degrees) to use when generating island orientations which will be considered during packing"

    ISLAND_ROT_STEP_ENABLE_NAME='Enable Island Rotation Step'
    ISLAND_ROT_STEP_ENABLE_DESC="Enable per-island rotation step"

    ISLAND_ROT_STEP_NAME='Rotation Step Value (d)'
    ISLAND_ROT_STEP_DESC="Rotation step value (in degrees) to be set for the selected islands"

    ISLAND_SCALE_LIMIT_ENABLE_NAME='Enable Island Scale Limit'
    ISLAND_SCALE_LIMIT_ENABLE_DESC="Enable per-island scale limit (in percentage)"

    ISLAND_SCALE_LIMIT_NAME='Scale Limit Value (%)'
    ISLAND_SCALE_LIMIT_DESC="Scale limit value (in percentage) to be set for the selected islands"

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

    TILE_COUNT_NAME="Tile Count"
    TILE_COUNT_DESC="Determines the number of tiles the given group will be packed into"

    GROUP_METHOD_NAME="Grouping Method"
    GROUP_METHOD_DESC="Grouping method to use"

    GROUP_METHOD_MATERIAL_DESC = 'Islands sharing the same material will belong to the same group'
    GROUP_METHOD_SIMILARITY_DESC = 'Islands of a similar shape will belong to the same group'
    GROUP_METHOD_MESH_DESC = 'Islands being part of adjacent geometry will belong to the same group'
    GROUP_METHOD_OBJECT_DESC = 'Islands being part of the same object will belong to the same group'
    GROUP_METHOD_MANUAL_DESC = "Grouping is determined manually by the user using a grouping scheme"
    GROUP_METHOD_TILE_DESC = 'Islands placed in the same UDIM tile will belong to the same group'

    GROUP_LAYOUT_MODE_NAME = 'Group Layout Mode'
    GROUP_LAYOUT_MODE_DESC = 'Determines where in the UV space the particular groups will be packed'

    TILES_IN_ROW_NAME="Tiles In Row"
    TILES_IN_ROW_DESC="Determines the maximum number of tiles in a single tile row. After all tiles in the given row are used, further UV islands will be packed into the tiles from the next row"

    GROUP_LAYOUT_MODE_AUTOMATIC_DESC="Groups will be automatically packed one after another. The number of tiles for each group is determined by the '{}' parameter. The maximum number of tiles in a single row is determined by the '{}' parameter".format(TILE_COUNT_NAME, TILES_IN_ROW_NAME)
    GROUP_LAYOUT_MODE_MANUAL_DESC="Determine target boxes for each group manually"
    GROUP_LAYOUT_MODE_AUTOMATIC_HORI_DESC="Every group will be automatically packed into the distinct tile row (first group into the first row, second group into the second row etc). The number of tiles for each group is determined by the '{}' parameter".format(TILE_COUNT_NAME)
    GROUP_LAYOUT_MODE_AUTOMATIC_VERT_DESC="Every group will be automatically packed into the distinct tile column (first group into the first column, second group into the second column etc). The number of tiles for each group is determined by the '{}' parameter".format(TILE_COUNT_NAME)
    
    TEXEL_DENSITY_GROUP_POLICY_NAME = 'Texel Density Policy'
    TEXEL_DENSITY_GROUP_POLICY_DESC = 'Determines how relative texel density of particular groups is processed'

    TEXEL_DENSITY_GROUP_POLICY_INDEPENDENT_NAME = 'Independent'
    TEXEL_DENSITY_GROUP_POLICY_UNIFORM_NAME = 'Uniform'
    TEXEL_DENSITY_GROUP_POLICY_CUSTOM_NAME = 'Custom'

    TEXEL_DENSITY_CLUSTER_NAME='Texel Density Cluster'
    TEXEL_DENSITY_CLUSTER_DESC="If given groups have the same value of this parameter set, then uniform scaling will be applied to them during packing (their relative texel density will be maintained). This per-group parameter is only used if '{}' is set to '{}'".format(TEXEL_DENSITY_GROUP_POLICY_NAME, TEXEL_DENSITY_GROUP_POLICY_CUSTOM_NAME)

    TEXEL_DENSITY_GROUP_POLICY_INDEPENDENT_DESC = 'Relative texel density of the groups will NOT be maintained (all groups are scaled independently during packing)'
    TEXEL_DENSITY_GROUP_POLICY_UNIFORM_DESC = 'Relative texel density of the groups will be maintained (uniform scale will be applied to all groups during packing)'
    TEXEL_DENSITY_GROUP_POLICY_CUSTOM_DESC = "Determine manually which groups will have relative texel density maintained. Given groups will have relative texel density maintained during packing (the same scale will be applied to them) if they share the same value of the '{}' per-group parameter".format(TEXEL_DENSITY_CLUSTER_NAME)

    GROUP_COMPACTNESS_NAME="Grouping Compactness"
    GROUP_COMPACTNESS_DESC="A value from 0 to 1 specifying how much the packer should prefer solutions providing more compact grouping, when packing groups together. A lower value means the packer will strive less to achieve compact grouping, at the same time it will prioritize achieving better coverage of the overall packing. With a greater value of the parameter, groups will be packed more compactly, but the coverage of the entire solution might be worse. WARNING: use this parameter with care - a small increase of its value might considerably change the result you will get"

    MANUAL_GROUP_NUM_NAME="Group Number"
    MANUAL_GROUP_NUM_DESC="Manual group number to be assigned to the selected islands"

    LOCK_GROUPS_ENABLE_NAME='Enable Lock Groups'
    LOCK_GROUPS_ENABLE_DESC="Specify manually which islands will be locked together during packing"

    LOCK_GROUP_NUM_NAME="Lock Group Number"
    LOCK_GROUP_NUM_DESC="Lock group number to be assigned to the selected islands"

    USE_BLENDER_TILE_GRID_NAME="Use Blender UDIM Grid"
    USE_BLENDER_TILE_GRID_DESC="If enabled, the tile grid shape is determined by the Blender UV editor settings (N-panel / View tab). Otherwise, the shape is configured using the properties below"

    TILE_COUNT_PER_GROUP_NAME="Tile Count Per Group"
    TILE_COUNT_PER_GROUP_DESC="Determines the number of tiles every group will be packed into"

    LOCK_OVERLAPPING_ENABLE_NAME='Lock Overlapping Enable'
    LOCK_OVERLAPPING_ENABLE_DESC='Treat overlapping islands as a single island'

    LOCK_OVERLAPPING_MODE_NAME='Lock Overlapping Mode'
    LOCK_OVERLAPPING_MODE_DESC='Determines when two islands are locked together by the packer'

    LOCK_OVERLAPPING_MODE_ANY_PART_DESC="Two islands will be locked together if only they overlap by any part"
    LOCK_OVERLAPPING_MODE_EXACT_DESC="Two islands will be locked together only if they have the same bounding boxes in the UV space and have identical area"

    PRE_VALIDATE_NAME='Automatic UV Pre-Validation'
    PRE_VALIDATE_DESC='Automatically validate the UV map before packing. If any invalid UV face is found during validation, packing will be aborted and the given UV faces will be selected. WARNING: enabling this option may increase the packing initialization time for UV maps with the huge number of faces, use it with care'

    HEURISTIC_ENABLE_NAME='Enable Heuristic'
    HEURISTIC_ENABLE_DESC="Perform multiple packing iterations in order to find the optimal result"

    HEURISTIC_SEARCH_TIME_NAME='Search Time (s)'
    HEURISTIC_SEARCH_TIME_DESC='Specify a time in seconds for the heuristic search. After timeout is reached the packer will stop and the best result will be applied to the UV map. If the time is set to 0 the packer will perfrom the search continuously, until the user manually applies the result by pressing ESC'

    HEURISTIC_MAX_WAIT_TIME_NAME='Max Wait Time (s)'
    HEURISTIC_MAX_WAIT_TIME_DESC="Maximal time the packer will wait for a better result. If the heuristic algorithm is not able to find a tighter packing during that time, the operation will be automatically finished and the best result found so far will be applied to the UV map. If set to 0, then the functionality will be disabled"

    ADVANCED_HEURISTIC_NAME='Advanced Heuristic'
    ADVANCED_HEURISTIC_DESC="Use an advanced method during a heuristic search. With this option enabled add-on will examine a broader set of solutions when searching for the optimal one. This method is most useful when packing a limited number of islands - in such case it allows to find a better solution than if using the simple method. Enabling this option is not recommended when packing a UV map containing a greater number of islands"

    SIMI_THRESHOLD_NAME='Similarity Threshold'
    SIMI_THRESHOLD_DESC="A greater value of this parameter means islands will be more likely recognized as a similar in shape. A lower value means more accurate distinction. For more info regarding similarity detection click the help button"

    SIMI_ADJUST_SCALE_NAME='Adjust Scale'
    SIMI_ADJUST_SCALE_DESC='Scale islands to the same size before determining whether they are similar'

    SIMI_CHECK_VERTICES_NAME='Check Vertices'
    SIMI_CHECK_VERTICES_DESC='Consider islands as similar only if they have matching vertices (not only outer shape)'

    SIMI_CORRECT_VERTICES_NAME='Correct Vertices'
    SIMI_CORRECT_VERTICES_DESC="Correct position of matching UV vertices of similar islands so they are placed on the top of each other after aligning. This option is only available when the '{}' option is enabled".format(SIMI_CHECK_VERTICES_NAME)

    SIMI_VERTEX_THRESHOLD_NAME='Vertex Threshold'
    SIMI_VERTEX_THRESHOLD_DESC='Maximum distance below which two vertices are considered as matching'

    ALIGN_PRIORITY_ENABLE_NAME='Enable Align Priority'
    ALIGN_PRIORITY_ENABLE_DESC='Control which island is aligned (moved) onto another when two islands are considered similar by the packer (check the mode documentation for more details)'

    ALIGN_PRIORITY_NAME='Align Priority'
    ALIGN_PRIORITY_DESC='Align priority value to assign'

    FULLY_INSIDE_NAME='Only Islands Fully Inside'
    FULLY_INSIDE_DESC="Process only islands which are fully inside the UV target box"

    MOVE_ISLANDS_NAME='Move Box With Islands'
    MOVE_ISLANDS_DESC="Move the UV target box together with selected islands inside"

    TILE_X_NAME='Tile (X)'
    TILE_X_DESC='X coordinate of a tile to be set'

    TILE_Y_NAME='Tile (Y)'
    TILE_Y_DESC='Y coordinate of a tile to be set'

    CUSTOM_TARGET_BOX_ENABLE_NAME='Enable Custom Target Box'
    CUSTOM_TARGET_BOX_ENABLE_DESC='Pack to a custom box in the UV space'

    OVERRIDE_GLOBAL_OPTIONS_NAME='Override Global Options'
    OVERRIDE_GLOBAL_OPTIONS_DESC='Enable overriding of the global options for the given group'
    OVERRIDE_GLOBAL_OPTION_DESC='Override the given option for the given group'

    LAST_GROUP_COMPLEMENTARY_SUPPORTED_MSG="Supported only if '{}' is set to '{}' and the grouping scheme has at least 2 groups".format(TEXEL_DENSITY_GROUP_POLICY_NAME, TEXEL_DENSITY_GROUP_POLICY_UNIFORM_NAME)
    LAST_GROUP_COMPLEMENTARY_NAME='Last Group As Complementary'
    LAST_GROUP_COMPLEMENTARY_DESC="Automatically pack the last group on the top of all other groups. {}".format(LAST_GROUP_COMPLEMENTARY_SUPPORTED_MSG)

    GROUPS_TOGETHER_CONFIRM_MSG = 'WARNING: packing groups together requires the heuristic search to produce an optimal result - it is strongy recommended to enable it before continuing. Press OK to continue, click outside the pop-up to cancel the operation'

    SEED_NAME='Seed'
    TEST_PARAM_NAME='Test Parameter'
    WRITE_TO_FILE_NAME='Write UV Data To File'
    SIMPLIFY_DISABLE_NAME='Simplify Disable'
    WAIT_FOR_DEBUGGER_NAME='Wait For Debugger'

    APPEND_MODE_NAME_TO_OP_LABEL_NAME="Append Mode To Operator Name"
    APPEND_MODE_NAME_TO_OP_LABEL_DESC="This option should only be enabled temporarily, only for the time when you want to add an UVPackmaster operator to Quick Favorites. If you add an operator with this option enabled, the selected mode name will be permanently appended to the operator name in the Quick Favorites list. After the operator was added, you can disable this option immediately"

    BOX_RENDER_LINE_WIDTH_NAME="Box Border Width"
    BOX_RENDER_LINE_WIDTH_DESC="Determines the width of box borders rendered in the UV editor during the operation. WARNING: setting width to a low value is not recommended"


class PropConstants:

    ROTATION_ENABLE_DEFAULT = True
    PRE_ROTATION_DISABLE_DEFAULT = False

    ROTATION_STEP_MIN = 1
    ROTATION_STEP_MAX = 180
    ROTATION_STEP_DEFAULT = 90

    PIXEL_MARGIN_MIN = 1
    PIXEL_MARGIN_MAX = 100
    PIXEL_MARGIN_DEFAULT = 5

    PIXEL_PADDING_MIN = 0
    PIXEL_PADDING_MAX = 100
    PIXEL_PADDING_DEFAULT = 0

    EXTRA_PIXEL_MARGIN_TO_OTHERS_MIN = 0
    EXTRA_PIXEL_MARGIN_TO_OTHERS_MAX = 100
    EXTRA_PIXEL_MARGIN_TO_OTHERS_DEFAULT = 0

    PIXEL_MARGIN_TEX_SIZE_MIN = 16
    PIXEL_MARGIN_TEX_SIZE_MAX = 16384	
    PIXEL_MARGIN_TEX_SIZE_DEFAULT = 1024

    TILES_IN_ROW_DEFAULT = 10
    TILE_COUNT_PER_GROUP_DEFAULT = 1
    LAST_GROUP_COMPLEMENTARY_DEFAULT = False
    GROUP_COMPACTNESS_DEFAULT = 0.0
    