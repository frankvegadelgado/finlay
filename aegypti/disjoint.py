import numpy as np

class FastCliqueUF:
    """
    A Union-Find structure that only merges components if the union
    induces a clique in the underlying graph. All clique checks and
    component updates are accelerated using numpy.uint64 SIMD blocks,
    giving O(k / w) merge time where w = 64 bits per block.
    """

    def __init__(self, graph):
        self.graph = graph
        self.nodes = list(graph.nodes())
        self.index = {u: i for i, u in enumerate(self.nodes)}
        self.n = len(self.nodes)

        # Number of 64-bit blocks needed to represent n bits
        self.blocks = (self.n + 63) // 64

        # Standard Union-Find parent + size
        self.parent = {u: u for u in self.nodes}
        self.size = {u: 1 for u in self.nodes}

        # Precompute adjacency bitsets for each node as numpy uint64 arrays
        self.adj = {}
        for u in self.nodes:
            arr = np.zeros(self.blocks, dtype=np.uint64)
            for v in graph.neighbors(u):
                idx = self.index[v]
                arr[idx // 64] |= np.uint64(1) << (idx % 64)
            # A node is always adjacent to itself for clique purposes
            idx = self.index[u]
            arr[idx // 64] |= np.uint64(1) << (idx % 64)
            self.adj[u] = arr

        # Component bitsets: which nodes are in the component
        self.comp_bit = {
            u: self._singleton_bitset(u) for u in self.nodes
        }

        # Component adjacency intersection bitsets
        self.comp_adj = {
            u: self.adj[u].copy() for u in self.nodes
        }

    def _singleton_bitset(self, u):
        """Return a bitset with only node u set."""
        arr = np.zeros(self.blocks, dtype=np.uint64)
        idx = self.index[u]
        arr[idx // 64] |= np.uint64(1) << (idx % 64)
        return arr

    def find(self, u):
        """Path-compressed find."""
        if self.parent[u] != u:
            self.parent[u] = self.find(self.parent[u])
        return self.parent[u]

    def union(self, u, v):
        """
        Merge the components of u and v only if the union forms a clique.
        Return True iff the resulting clique has size >= 3.
        All clique checks and bitset merges are SIMD-accelerated.
        """
        ru, rv = self.find(u), self.find(v)
        if ru == rv:
            # Already in same component → check if size >= 3
            return self.size[ru] >= 3

        # Union-by-size heuristic
        if self.size[ru] < self.size[rv]:
            ru, rv = rv, ru

        # Proposed merged component bitset
        merged_bit = self.comp_bit[ru] | self.comp_bit[rv]

        # Intersection of adjacency bitsets of both components
        merged_adj = self.comp_adj[ru] & self.comp_adj[rv]

        # Clique condition:
        # merged_bit must be subset of merged_adj
        if np.any(merged_bit & ~merged_adj):
            return False  # Reject merge: not a clique

        # Accept merge
        self.parent[rv] = ru
        new_size = self.size[ru] + self.size[rv]
        self.size[ru] = new_size

        # Update component bitset
        self.comp_bit[ru] = merged_bit

        # Update adjacency intersection
        self.comp_adj[ru] = merged_adj

        # Return True only if the resulting clique has size >= 3
        return new_size >= 3


    def to_sets(self):
        """
        Return all disjoint sets after full path compression.
        This reconstructs components by grouping nodes by their root.
        """
        groups = {}
        for u in self.nodes:
            r = self.find(u)
            groups.setdefault(r, set()).add(u)
        return list(groups.values())
