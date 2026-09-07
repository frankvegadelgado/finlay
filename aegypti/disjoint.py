class FastCliqueUF:
    """
    A Union-Find structure that only merges components if the union
    induces a clique in the underlying graph. 
    Bitwise operations leverage Python's native arbitrary-precision integers
    to achieve O(1) checks.
    """

    def __init__(self, graph):
        """
        Runtime: O(N * d) where N is the number of nodes and d is the maximum degree.
        Precomputes the bitmasks as large Python integers.
        """
        self.graph = graph
        self.nodes = list(graph.nodes())
        self.index = {u: i for i, u in enumerate(self.nodes)}
        self.n = len(self.nodes)

        self.parent = {u: u for u in self.nodes}

        # Precompute adjacency bitsets for each node as a single Python integer (bitmask)
        self.adj_mask = {}
        for u in self.nodes:
            mask = 0
            for v in graph.neighbors(u):
                mask |= (1 << self.index[v])
            mask |= (1 << self.index[u])
            self.adj_mask[u] = mask
        
        self.added_mask = 0

    def find(self, u):
        """
        Runtime: Amortized O(alpha(N)), where alpha is the inverse Ackermann function.
        Path-compressed find.
        """
        if self.parent[u] != u:
            self.parent[u] = self.find(self.parent[u])
        return self.parent[u]

    def add(self, u):
        """
        Runtime: O(1).
        Adds a node 'u' to the structure. Returns True if there is at least one edge 
        between 'u' and any previously added element, False otherwise.
        """
        u_bit = 1 << self.index[u]
        overlap = self.added_mask & self.adj_mask[u]
        has_edge = bool(overlap & ~u_bit)
        self.added_mask |= u_bit
        
        return has_edge

    def remove(self, u):
        """
        Runtime: O(1).
        Removes a node 'u' from the added elements by clearing its corresponding bit.
        """
        self.added_mask &= ~(1 << self.index[u])

    def to_sets(self):
        """
        Runtime: O(N^2 * alpha(N)).
        Builds the connected components by evaluating the edges of the currently 
        added nodes, strictly enforcing that each merged component remains a clique.
        """
        self.parent = {u: u for u in self.nodes}
        
        # Temporary structures to validate cliques during reconstruction
        comp_mask = {u: (1 << self.index[u]) for u in self.nodes}
        comp_adj = {u: self.adj_mask[u] for u in self.nodes}
        
        added_nodes = [u for u in self.nodes if self.added_mask & (1 << self.index[u])]
        n_added = len(added_nodes)
        
        for i in range(n_added):
            for j in range(i + 1, n_added):
                u = added_nodes[i]
                v = added_nodes[j]
                
                # If there is an original edge between u and v
                if self.adj_mask[u] & (1 << self.index[v]):
                    ru = self.find(u)
                    rv = self.find(v)
                    
                    if ru != rv:
                        merged_mask = comp_mask[ru] | comp_mask[rv]
                        merged_adj = comp_adj[ru] & comp_adj[rv]
                        
                        # Strict Clique condition: the merged mask must be
                        # a subset of the merged adjacencies.
                        if not (merged_mask & ~merged_adj):
                            self.parent[ru] = rv
                            comp_mask[rv] = merged_mask
                            comp_adj[rv] = merged_adj
                        
        groups = {}
        for u in added_nodes:
            r = self.find(u)
            groups.setdefault(r, set()).add(u)
            
        return list(groups.values())