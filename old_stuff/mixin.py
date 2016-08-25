class EqualityMixin(object):

    def __eq__(self, other):
        return type(self) == type(other) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

class StrMixin(object):

    def __repr__(self):
        return self.__class__.__name__ + str(self.__dict__)    


