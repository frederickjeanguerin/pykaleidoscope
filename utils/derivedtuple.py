from collections import namedtuple

def derivedtuple(typename, properties, *parents):
    """Create a new namedtuple with ancestors in parents."""
    nt = namedtuple(typename, properties)
    # Add parents
    nt.__bases__ = tuple(parents) + nt.__bases__
    # Add method Flatten
    # setattr(nt, 'flatten', _flatten)
    return nt

