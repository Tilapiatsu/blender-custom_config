# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

# Contact for more information about the Addon:
# Email:    germano.costa@ig.com.br
# Twitter:  wii_mano @mano_wii

import bgl
import ctypes
import numpy as np


# figure out side of _Py_ssize_t
if hasattr(ctypes.pythonapi, 'Py_InitModule4_64'):
    _Py_ssize_t = ctypes.c_int64
else:
    _Py_ssize_t = ctypes.c_int


class _PyObject(ctypes.Structure):
    pass


_PyObject._fields_ = [
    ('ob_refcnt', _Py_ssize_t),
    ('ob_type', ctypes.POINTER(_PyObject)),
]


if object.__basicsize__ != ctypes.sizeof(_PyObject):
    # python with trace
    class _PyObject(ctypes.Structure):
        _fields_ = [
            ('_ob_next', ctypes.POINTER(_PyObject)),
            ('_ob_prev', ctypes.POINTER(_PyObject)),
            ('ob_refcnt', _Py_ssize_t),
            ('ob_type', ctypes.POINTER(_PyObject)),
        ]


class _PyVarObject(_PyObject):
    _fields_ = [
        ('ob_size', _Py_ssize_t),
    ]


class CBuffer(_PyVarObject):
    _fields_ = [
        ("parent", ctypes.py_object),
        ("type", ctypes.c_int),
        ("ndimensions", ctypes.c_int),
        ("dimensions", ctypes.POINTER(ctypes.c_int)),
        ("buf", ctypes.c_void_p),
    ]


assert ctypes.sizeof(CBuffer) == bgl.Buffer.__basicsize__


class VoidBufValue:
    def __init__(self, value):
        self.buf = bgl.Buffer(bgl.GL_BYTE, 1)

        self._buf_addr = ctypes.pointer(ctypes.c_void_p.from_address(id(self.buf) + CBuffer.buf.offset))
        self._allocated_buf = self._buf_addr[0]
        self._buf_addr[0] = value

    def __del__(self):
        self._buf_addr[0] = self._allocated_buf
        # del self._allocated_buf
        # del self._buf_addr
        del self.buf


def np_array_as_bgl_Buffer(array):
    typ = array.dtype
    if typ == np.int8:
        typ = bgl.GL_BYTE
    elif typ == np.int16:
        typ = bgl.GL_SHORT
    elif typ == np.int32:
        typ = bgl.GL_INT
    elif typ == np.float32:
        typ = bgl.GL_FLOAT
    elif typ == np.float64:
        typ = bgl.GL_DOUBLE
    else:
        raise Exception("Unsupported type %s" % typ)

    _decref = ctypes.pythonapi.Py_DecRef
    _incref = ctypes.pythonapi.Py_IncRef

    _decref.argtypes = _incref.argtypes = [ctypes.py_object]
    _decref.restype = _incref.restype = None

    buf = bgl.Buffer(bgl.GL_BYTE, (1, *array.shape))[0]
    c_buf = CBuffer.from_address(id(buf))

    _decref(c_buf.parent)
    _incref(array)

    c_buf.parent = array   # Prevents MEM_freeN
    c_buf.type = typ
    c_buf.buf = array.ctypes.data

    return buf
