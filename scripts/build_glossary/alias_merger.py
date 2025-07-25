from collections import defaultdict

class AliasMerger:
    def __init__(self):
        # This is an undirected graph where each alias is a node, and an edge connects aliases that refer to the same entity.
        self.alias_graph = defaultdict(set)

    def add_aliases(self, raw_dict):
        """Takes raw alias mappings (dict[str, list[str]]) and builds internal graph."""
        for key, aliases in raw_dict.items():
            self.alias_graph[key]  # Ensure node is created, even with no aliases
            for alias in aliases:
                if alias:
                    self.alias_graph[key].add(alias)
                    self.alias_graph[alias].add(key)


    def merge(self):
        """
        Merges all connected aliases into canonical groups using DFS.

        Returns:
            dict[str, list[str]]: A dictionary where each key is the canonical name (lexically smallest in the group),
                                  and the value is a list of its aliases (excluding itself).
        """
        visited = set()  # Tracks visited nodes (aliases)
        merged_characters = []  # Stores groups of connected aliases

        def dfs(node, group):
            """
            Depth-First Search to collect all aliases connected to a given node.
            """
            if node not in visited:
                visited.add(node)
                group.add(node)
                for neighbor in self.alias_graph[node]:
                    dfs(neighbor, group)

        # Iterate through all nodes (aliases/names)
        for name in self.alias_graph:
            if name not in visited:
                group = set()
                dfs(name, group)  # Find all connected names/aliases
                merged_characters.append(sorted(group))  # Sort group for deterministic output

        # Convert groups to canonical dict
        canonical_dict = {}
        for group in merged_characters:
            main = group[0]  # The canonical name is the lexicographically smallest one
            canonical_dict[main] = sorted(set(group) - {main})  # Exclude the canonical name from its alias list

        return canonical_dict
