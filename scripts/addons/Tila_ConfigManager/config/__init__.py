def get_addon_list() -> str:
    from pathlib import Path
    path = str(Path(__file__).parent/'AddonList.json')
    return path

AL = get_addon_list()