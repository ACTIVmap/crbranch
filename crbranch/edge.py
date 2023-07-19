
class Edge:
    
    def __init__(self, n1, n2):
        self.n1 = n1
        self.n2 = n2

    def __eq__(self, other):
        if isinstance(other, Edge):
            v = other.to_array()
        else:
            v = other
        return (self.n1 == v[0] and self.n2 == v[1]) or (self.n1 == v[1] and self.n2 == v[0])

    def to_array(self):
        return [self.n1, self.n2]