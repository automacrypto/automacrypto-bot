import os
import yaml


def read_yaml(*directories: str, filename: str) -> object | None:
    file_diretory = os.path.join(directories, filename)
    memory_stream = open(f'{file_diretory}.yaml', 'r')

    try:
        file_object = yaml.safe_load(memory_stream)
    except:
        return None
    finally:
        memory_stream.close()

    return file_object
