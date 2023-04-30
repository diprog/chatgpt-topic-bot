import importlib
import glob
import os


def import_all(path):
    # get a handle on the module
    module = importlib.import_module(path)
    submodules = []
    for file in os.listdir(module.__path__[0]):
        if file.endswith('.py') and not file.startswith('__'):
            submodules.append(file[:-3])
    for submodule in submodules:
        submodule = importlib.import_module(path + '.' + submodule)


def import_module(path):
    module = importlib.import_module(path)