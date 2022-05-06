from os import listdir
from os.path import isfile, join

from utilities.yaml_helper import load_yaml

def load_macros(diretory: str, only_enabled: bool) -> dict:

    filenames = [filename for filename in listdir(diretory) if isfile(join(diretory, filename))]

    for filename in filenames:
        result = load_yaml(diretory, filename)

    return result
