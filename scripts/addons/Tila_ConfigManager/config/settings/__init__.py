from pathlib import Path
from Tila_ConfigManager.utils import get_module_members

settings = get_module_members(Path(__file__).parent, "settings")
