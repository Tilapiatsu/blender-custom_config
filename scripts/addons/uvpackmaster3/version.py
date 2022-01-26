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


from . import bl_info

class UvpmEditionInfo:
    suffix = None
    name = None
    long_name = None
    marker = None

    def __init__(self, _num, _suffix, _name, _long_name, _marker, _req_markers):
        self.num = _num
        self.suffix = _suffix
        self.name = _name
        self.long_name = _long_name
        self.marker = _marker
        self.req_markers = _req_markers


bl_info_version = bl_info['version']

class UvpmVersionInfo:
    ADDON_VERSION_MAJOR = bl_info_version[0]
    ADDON_VERSION_MINOR = bl_info_version[1]
    ADDON_VERSION_PATCH = bl_info_version[2]

    ENGINE_VERSION_MAJOR = ADDON_VERSION_MAJOR
    ENGINE_VERSION_MINOR = ADDON_VERSION_MINOR
    ENGINE_VERSION_PATCH = ADDON_VERSION_PATCH

    PRESET_VERSION_FIRST_SUPPORTED = 11
    PRESET_VERSION = 12
    GROUPING_SCHEME_VERSION = 1

    RELEASE_SUFFIX = ''

    @classmethod
    def release_suffix(cls):
        return cls.RELEASE_SUFFIX

    @classmethod
    def addon_version_tuple(cls):
        return (cls.ADDON_VERSION_MAJOR, cls.ADDON_VERSION_MINOR, cls.ADDON_VERSION_PATCH)

    @classmethod
    def addon_version_string(cls):
        return '{}.{}.{}'.format(cls.ADDON_VERSION_MAJOR, cls.ADDON_VERSION_MINOR, cls.ADDON_VERSION_PATCH)

    @classmethod
    def addon_version_release_string(cls):
        version_str = cls.addon_version_string()
        release_str = cls.release_suffix()

        return version_str if release_str == '' else (version_str + '-' + release_str)

    @classmethod
    def engine_version_tuple(cls):
        return (cls.ENGINE_VERSION_MAJOR, cls.ENGINE_VERSION_MINOR, cls.ENGINE_VERSION_PATCH)

    @classmethod
    def engine_version_string(cls):
        return '{}.{}.{}'.format(cls.ENGINE_VERSION_MAJOR, cls.ENGINE_VERSION_MINOR, cls.ENGINE_VERSION_PATCH)

    @classmethod
    def uvpm_edition_array(cls):
        edition_array = [
            UvpmEditionInfo(1, 's', 'std', 'STD', 'UVPM_EDITION_STANDARD', []),
            UvpmEditionInfo(2, 'p', 'pro', 'PRO', 'UVPM_EDITION_PRO', []),
            UvpmEditionInfo(3, 'd', 'demo', 'DEMO', 'UVPM_EDITION_DEMO', [])
        ]

        return edition_array
