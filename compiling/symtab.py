TOO_FAR = 1000000    

class SymbolTable():


    def __init__(self):
        self.table = dict()

    @staticmethod
    def distance(given_types, expected_types, automatic_conversions = dict()):
        if len(given_types) != len(expected_types):
            return TOO_FAR
        dist = 0
        for given, expected in zip(given_types, expected_types):
            if given != expected:
                if automatic_conversions.get((given, expected)):
                    dist += 1
                else:
                    return TOO_FAR
        return dist    


    def find(self, name, arg_types = tuple(), aliases = dict(), automatic_promotions = dict()):
        """ Tries to find the associated symbol given its name and arg_types
            
            On success, return (symbol, None)
            On failure, return either (None, None) if name is not found
            or (None, symlist), if the name was found but not type matched.
            
            The symbols are searched from more recent to older, 
            and the first fittest match is returned.
        """

        # Find the list of available symbols with the same name
        symlist = self.table.get(name)
        if not symlist:
            # try to find an alias
            alias = aliases.get(name)
            if alias:
                symlist = self.table.get(alias)

        # If not found, return nothing        
        if not symlist:
            return None, None

        # Search for the most suitable variant in the list
        best_dist = TOO_FAR
        best_match = None    
        for sym in reversed(symlist):
            dist = SymbolTable.distance(arg_types, sym.arg_types, automatic_promotions)
            if dist < best_dist:
                best_dist = dist
                best_match = sym
        return best_match, symlist        


    def add(self, symbol):
        """ Adds a symbol to the table. 
            This is a O(1) operation. 
        """
        
        assert hasattr(symbol, 'name')
        assert hasattr(symbol, 'arg_types')

        # If first symbol with that name, 
        # create a list before adding the symbol
        if not self.table.get(symbol.name):
            self.table[symbol.name] = []
        self.table[symbol.name].append(symbol) 


    def remove(self, symbol):
        """ Remove a given symbol from the table
            The search starts from the end of the list 
            so removing a recent symbol is much faster, about O(1)
        """
        symlist = self.table[symbol.name]
        last_index = len(symlist) - 1
        for i, sym in enumerate(reversed(symlist)):
            if sym == symbol:
                del symlist[last_index - i]
                if not symlist:
                    del self.table[symbol.name]
                return
        assert False, "symbol not found: " + str(symbol)        


    def __repr__(self):
        repr = ""
        for key in sorted(self.table.keys()):
            for sym in reversed(self.table[key]):
                repr += str(sym) + "\n"
        return repr        

SYMTAB = SymbolTable()
