import bpy
from bpy.props import FloatProperty

import struct

from .utils import ShadowedPropertyGroupMeta, ShadowedPropertyGroup, get_prefs


DEFAULT_TARGET_BOX_MIN_X = 0.0
DEFAULT_TARGET_BOX_MIN_Y = 0.0
DEFAULT_TARGET_BOX_MAX_X = 1.0
DEFAULT_TARGET_BOX_MAX_Y = 1.0

def mark_boxes_dirty(self, context):
    get_prefs().boxes_dirty = True


def _box_coord_update(self, context, coord_name):
    coord_val = float(getattr(self, coord_name))
    coord_val_rounded = round(coord_val, self.COORD_PRECISION)

    # Cast the value to single precision because Blender internally uses 
    # single precision to store a property value
    coord_val_rounded = struct.unpack('f', struct.pack('f', coord_val_rounded))[0]
    # print('coord_val: {:.100}'.format(coord_val))
    # print('coord_val_rounded: {:.100}'.format(coord_val_rounded))
    if coord_val != coord_val_rounded:
        setattr(self, coord_name, coord_val_rounded)

    mark_boxes_dirty(self, context)


def _p1_x_update(self, context):
    _box_coord_update(self, context, 'p1_x')

def _p1_y_update(self, context):
    _box_coord_update(self, context, 'p1_y')

def _p2_x_update(self, context):
    _box_coord_update(self, context, 'p2_x')

def _p2_y_update(self, context):
    _box_coord_update(self, context, 'p2_y')



class UVPM3_Box(ShadowedPropertyGroup, metaclass=ShadowedPropertyGroupMeta):

    DIMENSION_MIN_LIMIT = 0.05
    COORD_PRECISION = 2
    COORD_STEP = 10.0
    COOORD_TO_STR_FORMAT = "{:." + str(COORD_PRECISION) + "}"

    p1_x : FloatProperty(name="P1 (X)", default=DEFAULT_TARGET_BOX_MIN_X, precision=COORD_PRECISION, step=COORD_STEP, update=_p1_x_update)
    p1_y : FloatProperty(name="P1 (Y)", default=DEFAULT_TARGET_BOX_MIN_Y, precision=COORD_PRECISION, step=COORD_STEP, update=_p1_y_update)
    p2_x : FloatProperty(name="P2 (X)", default=DEFAULT_TARGET_BOX_MAX_X, precision=COORD_PRECISION, step=COORD_STEP, update=_p2_x_update)
    p2_y : FloatProperty(name="P2 (Y)", default=DEFAULT_TARGET_BOX_MAX_Y, precision=COORD_PRECISION, step=COORD_STEP, update=_p2_y_update)

    def __init__(
        self,
        p1_x=DEFAULT_TARGET_BOX_MIN_X,
        p1_y=DEFAULT_TARGET_BOX_MIN_Y,
        p2_x=DEFAULT_TARGET_BOX_MAX_X,
        p2_y=DEFAULT_TARGET_BOX_MAX_Y):

        self.p1_x = p1_x
        self.p1_y = p1_y
        self.p2_x = p2_x
        self.p2_y = p2_y

    def __hash__(self):
        return hash(self.coords_tuple())

    def __eq__(self, other):
        return self.coords_tuple() == other.coords_tuple()

    def __ne__(self, other):
        return not(self == other)

    def validate(self):

        if self.width < self.DIMENSION_MIN_LIMIT:
            raise RuntimeError('UV target box width must be larger than ' + self.DIMENSION_MIN_LIMIT)

        if self.height < self.DIMENSION_MIN_LIMIT:
            raise RuntimeError('UV target box height must be larger than ' + self.DIMENSION_MIN_LIMIT)

    def coord_to_str(self, coord):
        return self.COOORD_TO_STR_FORMAT.format(coord)

    @property
    def min_corner(self):
        return min(self.p1_x, self.p2_x), min(self.p1_y, self.p2_y)

    @property
    def max_corner(self):
        return max(self.p1_x, self.p2_x), max(self.p1_y, self.p2_y)

    @property
    def width_interval(self):
        return min(self.p1_x, self.p2_x), max(self.p1_x, self.p2_x)

    @property
    def height_interval(self):
        return min(self.p1_y, self.p2_y), max(self.p1_y, self.p2_y)

    @property
    def width(self):
        return abs(self.p1_x - self.p2_x)

    @property
    def height(self):
        return abs(self.p1_y - self.p2_y)

    def offset(self, offset):

        self.p1_x += offset[0]
        self.p2_x += offset[0]
        self.p1_y += offset[1]
        self.p2_y += offset[1]

    def to_string(self):

        min_corner = self.min_corner
        max_corner = self.max_corner

        return "{}:{}:{}:{}".format(
            self.coord_to_str(min_corner[0]),
            self.coord_to_str(min_corner[1]),
            self.coord_to_str(max_corner[0]),
            self.coord_to_str(max_corner[1]))

    def coords_tuple(self):

        min_corner = self.min_corner
        max_corner = self.max_corner
        return (min_corner[0], min_corner[1], max_corner[0], max_corner[1])

    def label(self):

        min_corner = self.min_corner
        max_corner = self.max_corner

        min_corner_i = tuple(int(x) for x in min_corner)
        max_corner_i = tuple(int(x) for x in max_corner)

        if min_corner_i == min_corner and max_corner_i == max_corner:
            min_corner_i_plus1 = tuple(i + 1 for i in min_corner_i)
            if min_corner_i_plus1 == max_corner_i:
                return "Tile {}:{}".format(min_corner_i[0], min_corner_i[1])

        return "[{}, {}]-[{}, {}]".format(
            self.coord_to_str(min_corner[0]),
            self.coord_to_str(min_corner[1]),
            self.coord_to_str(max_corner[0]),
            self.coord_to_str(max_corner[1]))

    def tile(self, tile_x, tile_y):

        min_corner = self.min_corner
        max_corner = self.max_corner

        width = self.width
        height = self.height

        tile_max = (max_corner[0] + width * tile_x, max_corner[1] + height * tile_y)
        tile_min = (min_corner[0] + width * tile_x, min_corner[1] + height * tile_y)

        return UVPM3_Box(tile_min[0], tile_min[1], tile_max[0], tile_max[1])

    def tile_from_num(self, tile_num, tiles_in_row):

        assert(tiles_in_row > 0)
        tile_x = tile_num % tiles_in_row
        tile_y = tile_num // tiles_in_row

        return self.tile(tile_x, tile_y)

    def point_inside(self, coords):

        min_corner = self.min_corner
        max_corner = self.max_corner

        return\
            min_corner[0] < coords[0] and\
            min_corner[1] < coords[1] and\
            max_corner[0] > coords[0] and\
            max_corner[1] > coords[1]

    def point_on_edges(self, coords, thickness):
        thickness = thickness / 2

        left = self.p1_x - thickness
        left_prim = self.p1_x + thickness

        top = self.p2_y + thickness
        top_prim = self.p2_y - thickness

        right = self.p2_x + thickness
        right_prim = self.p2_x - thickness

        bottom = self.p1_y - thickness
        bottom_prim = self.p1_y + thickness

        if self.p1_x > self.p2_x:
            left, left_prim, right, right_prim = right_prim, right, left_prim, left
        if self.p1_y > self.p2_y:
            bottom, bottom_prim, top, top_prim = top_prim, top, bottom_prim, bottom

        on_left = min(left, left_prim) < coords[0] < max(left, left_prim) and min(top, bottom) < coords[1] < max(top, bottom)
        on_top = min(top, top_prim) < coords[1] < max(top, top_prim) and min(left, right) < coords[0] < max(left, right)
        on_right = min(right, right_prim) < coords[0] < max(right, right_prim) and min(top, bottom) < coords[1] < max(top, bottom) if not on_left else False
        on_bottom = min(bottom, bottom_prim) < coords[1] < max(bottom, bottom_prim) and min(left, right) < coords[0] < max(left, right) if not on_top else False

        if self.p1_x > self.p2_x:
            on_left, on_right = on_right, on_left
        if self.p1_y > self.p2_y:
            on_top, on_bottom = on_bottom, on_top

        return [on_left, on_top, on_right, on_bottom]

    @staticmethod
    def _interval_intersects(interval1, interval2):
        return not (interval1[0] >= interval2[1] or interval1[1] <= interval2[0])

    def intersects(self, other_box):
        return self._interval_intersects(self.width_interval, other_box.width_interval) \
               and self._interval_intersects(self.height_interval, other_box.height_interval)

    def copy_from(self, other):

        self.p1_x = float(other.p1_x)
        self.p2_x = float(other.p2_x)
        self.p1_y = float(other.p1_y)
        self.p2_y = float(other.p2_y)

    def copy(self):

        out = UVPM3_Box()
        out.copy_from(self)
        return out


DEFAULT_TARGET_BOX = UVPM3_Box(
                        p1_x=DEFAULT_TARGET_BOX_MIN_X,
                        p1_y=DEFAULT_TARGET_BOX_MIN_Y,
                        p2_x=DEFAULT_TARGET_BOX_MAX_X,
                        p2_y=DEFAULT_TARGET_BOX_MAX_Y)