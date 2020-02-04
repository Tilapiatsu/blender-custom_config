
from .blend import get_release_suffix

class UvpEditionInfo:
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


class UvpVersionInfo:
    ADDON_VERSION_MAJOR = 2
    ADDON_VERSION_MINOR = 3
    ADDON_VERSION_PATCH = 1

    UVP_VERSION_MAJOR = 2
    UVP_VERSION_MINOR = 3
    UVP_VERSION_PATCH = 1

    RELEASE_SUFFIX = get_release_suffix()

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
    def uvp_version_tuple(cls):
        return (cls.UVP_VERSION_MAJOR, cls.UVP_VERSION_MINOR, cls.UVP_VERSION_PATCH)

    @classmethod
    def uvp_version_string(cls):
        return '{}.{}.{}'.format(cls.UVP_VERSION_MAJOR, cls.UVP_VERSION_MINOR, cls.UVP_VERSION_PATCH)

    @classmethod
    def uvp_edition_array(cls):
        edition_array = [
            UvpEditionInfo(1, 's', 'std', 'standard', 'UVP_EDITION_STANDARD', []),
            UvpEditionInfo(2, 'p', 'pro', 'professional', 'UVP_EDITION_PRO', []),
            UvpEditionInfo(3, 'd', 'demo', 'DEMO', 'UVP_EDITION_DEMO', [])
        ]

        return edition_array
