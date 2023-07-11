from jsonpickle.pickler import Pickler
from jsonpickle.unpickler import Unpickler

pickler = Pickler(numeric_keys=True)
unpickler = Unpickler()


def flatten(obj):
    return pickler.flatten(obj)


def restore(obj):
    return unpickler.restore(obj)
