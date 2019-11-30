
import platform

if platform.system() == 'Linux':
    from .os_linux import *
elif platform.system() == 'Windows':
    from .os_windows import *
elif platform.system() == 'Darwin':
    from .os_mac import *