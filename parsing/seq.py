from .indenter import *

class Seq(SourceMixin):

    def __init__(self, items, first = None, last = None):
        assert isinstance(items, list)
        self.items = items
        assert first or last or len(items) > 0
        self.first_token = first or items[0].first_token
        self.last_token = last or items[-1].last_token   

    def to_code(self):
        return "(" + " ".join((item.to_code() for item in self.items)) + ")"    

    @property    
    def len(self):
        return len(self.items)    

