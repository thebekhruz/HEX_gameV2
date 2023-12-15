class disjoint_set():
    """
    Disjoint Set data structure used to find connections between cells
    """

    def __init__(self):
        """
        initialise parent and rank. add when necessary
        """
        self.parent = {}
        self.rank = {}

    def join(self, x, y):
        """
		Merge the groups of x and y if they were not already,
		return False if they were already merged, true otherwise
		"""

        rx = self.find(x)
        ry = self.find(y)

        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            self.parent[rx] = ry
        elif self.rank[rx] > self.rank[ry]:
            self.parent[ry] = rx
        else:
            self.parent[rx] = ry
            self.rank[ry] += 1
        return True

    def find(self, element):
        """
        Get the representative element associated with the set in
        which element resides.

        Compression of grandparent makes subsequent finds faster
        """
        if element not in self.parent:
            self.parent[element] = element
            self.rank[element] = 0

        p_element = self.parent[element]
        if element == p_element:
            return element

        g_element = self.parent[p_element]
        if g_element == p_element:
            return p_element

        self.parent[element] = g_element

        return self.find(g_element)

    def connected(self, x, y):
        """
        Check if two elements are in the same group.
        """
        return self.find(x) == self.find(y)
