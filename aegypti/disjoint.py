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


    def delete_edge(self, u, v):
        """
        Remove the edge (u, v) from the FastCliqueUF in-memory bitset
        structure. This does NOT modify the underlying NetworkX graph; it
        only clears the corresponding bits from adj[u]/adj[v] and from the
        component adjacency bitsets comp_adj[ru]/comp_adj[rv] so that
        future clique tests no longer treat (u, v) as an edge.

        Complexity:
          O(1) bit-flip work on the per-vertex adjacency bitsets, plus
          two O(blocks) updates to component adjacency bitsets if the
          two endpoints are in different singletons. In the regime where
          we use this (components of size <= 2 in Phase 1), the work is
          dominated by the O(n/w) component-bitset write, matching the
          existing per-union cost.

        Args:
            u, v: endpoint identifiers (must be existing nodes of the
                  underlying graph passed to __init__).
        """
        if u == v:
            return
        iu = self.index[u]
        iv = self.index[v]
        mask_u = np.uint64(1) << np.uint64(iu % 64)
        mask_v = np.uint64(1) << np.uint64(iv % 64)
        block_u = iu // 64
        block_v = iv // 64

        # Clear v from u's closed-neighbourhood bitset and vice versa.
        self.adj[u][block_v] &= ~mask_v
        self.adj[v][block_u] &= ~mask_u

        # Reflect the deletion in the *component* adjacency intersection
        # bitsets of u's and v's current roots. Each comp_adj is the AND
        # of the closed neighbourhoods of all vertices in the component;
        # clearing v from u's neighbourhood weakens u's contribution to
        # comp_adj[find(u)] at position v, and symmetrically.
        ru = self.find(u)
        rv = self.find(v)
        self.comp_adj[ru][block_v] &= ~mask_v
        if rv != ru:
            self.comp_adj[rv][block_u] &= ~mask_u

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
