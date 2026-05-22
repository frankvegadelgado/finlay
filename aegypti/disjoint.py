class FastCliqueUF:
    """
    A Union-Find structure that only merges components if the union
    induces a clique in the underlying graph.

    Phase 1 of the triangle finder first unions a maximal matching and
    then deletes rejected non-matching edges. Until a triangle is found,
    components normally stay small, so each clique check needs only a
    small number of edge-membership probes.
    """

    def __init__(self, graph):
        self.graph = graph
        self.nodes = list(graph.nodes())

        self.parent = {u: u for u in self.nodes}
        self.size = {u: 1 for u in self.nodes}
        self.members = {u: [u] for u in self.nodes}
        self.deleted_edges = set()

    @staticmethod
    def _edge_key(u, v):
        """Return an orientation-independent edge key for hashable nodes."""
        return frozenset((u, v))

    def _has_live_edge(self, u, v):
        """Return whether (u, v) exists and has not been deleted."""
        return self.graph.has_edge(u, v) and self._edge_key(u, v) not in self.deleted_edges

    def find(self, u):
        """Path-compressed find."""
        if self.parent[u] != u:
            self.parent[u] = self.find(self.parent[u])
        return self.parent[u]

    def union(self, u, v):
        """
        Merge the components of u and v only if the union forms a clique.
        Return True iff the resulting clique has size >= 3.
        """
        ru, rv = self.find(u), self.find(v)
        if ru == rv:
            return self.size[ru] >= 3

        if self.size[ru] < self.size[rv]:
            ru, rv = rv, ru

        for a in self.members[ru]:
            for b in self.members[rv]:
                if not self._has_live_edge(a, b):
                    return False

        self.parent[rv] = ru
        new_size = self.size[ru] + self.size[rv]
        self.size[ru] = new_size
        self.members[ru].extend(self.members[rv])
        del self.members[rv]

        return new_size >= 3

    def delete_edge(self, u, v):
        """
        Hide edge (u, v) from future FastCliqueUF clique tests.

        This does NOT modify the underlying NetworkX graph.
        """
        if u == v:
            return
        self.deleted_edges.add(self._edge_key(u, v))

    def to_sets(self):
        """Return all disjoint sets after full path compression."""
        groups = {}
        for u in self.nodes:
            r = self.find(u)
            groups.setdefault(r, set()).add(u)
        return list(groups.values())
