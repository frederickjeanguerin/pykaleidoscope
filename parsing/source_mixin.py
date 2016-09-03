
class SourceMixin:

    """ Can be mixed in with any class to provide
        useful properties about souce location of that object

        Requirements: 
            first_token and last_token properties should be defined.
    """

    def match(self, attribute):
        if isinstance(attribute, type):
            return isinstance(self, attribute)
        return False   

    @property     
    def pos(self):
        return self.first_token.pos

    @property     
    def endpos(self):
        return self.last_token.endpos             

    @property
    def source(self):
        return self.first_token.source    

    @property
    def text(self):
        return self.source[self.pos:self.endpos]

    @property
    def lineno(self):
        return self.first_token.lineno    

    @property
    def colno(self):
        return self.first_token.colno    

    def __str__(self):
        return "[{}] at {}:{}".format(self.text, self.lineno, self.colno)        
