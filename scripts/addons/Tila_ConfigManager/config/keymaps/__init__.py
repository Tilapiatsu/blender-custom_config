from pathlib import Path
from Tila_ConfigManager.utils import get_module_members

keymaps = get_module_members(Path(__file__).parent, 'keymaps')