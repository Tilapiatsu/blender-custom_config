import os

def get_path():
    return os.path.dirname(os.path.realpath(__file__))

AL = os.path.join(get_path(), 'AddonList.json')