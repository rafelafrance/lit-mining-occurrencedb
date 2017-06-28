"""So we can handle dictionary keys like object attributes."""


class DotDict(dict):
    """So we can handle dictionary keys like object attributes."""

    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dct=None):
        dict.__init__(self, dct)

        if dct is None:
            dct = {}

        for key, value in dct.items():
            if hasattr(value, 'keys'):
                value = DotDict(value)
            self[key] = value
