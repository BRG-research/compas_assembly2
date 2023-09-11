import uuid

# Path - Breanch, Element - Node Lead

class Assembly_Tree:
    def __init__(self, branch, twigs=None):
        self.branch = branch  # branch is empty if it is branch and not an element
        self.twigs = twigs if twigs is not None else []  # better have a sorted_dict <__str__, Assembly_Tree> currently only list(Assembly_Tree)
        self.parent = None
        self.is_leaf = False

    def add_child(self, child):
        child.parent = self
        self.twigs.append(child)

    @property
    def path(self):
        """The branch must have a meaning full string representation e.g. path_address
        path can be an index, an element type or any other string representation
        address is a memory value to identify duplicates
        """
        return str(self.branch)

    @property
    def path_str(self):
        return str(self.path)

    @property
    def level(self):
        level = 0
        p = self.parent
        while p:
            level = level + 1
            p = p.parent
        return level

    @property
    def depth(self):
        # Initialize depth to 0 and start from the current node
        depth = 0
        current_node = self

        # Backtrack to the root parent while incrementing depth
        while current_node.parent:
            depth += 1
            current_node = current_node.parent

        # Calculate the maximum depth by traversing twigs's subtrees
        return self._calculate_depth(self, depth)

    def _calculate_depth(self, node, depth):
        if not node.twigs:
            # If the node has no twigs, return the current depth
            return depth

        max_child_depth = depth
        for child in node.twigs:
            # Recursively calculate the depth for each child's subtree
            child_depth = self._calculate_depth(child, depth + 1)
            if child_depth > max_child_depth:
                max_child_depth = child_depth

        # Return the maximum depth among twigs's subtrees
        return max_child_depth

    def print_tree(self):
        prefix = "   " * self.level
        prefix = prefix + "|__ " if self.parent else ""
        print(prefix + self.path_str)
        if self.twigs:
            for child in self.twigs:
                child.print_tree()

    def merge_assemblies(self, a1, allow_duplicates=True):

        # Helper function to find a node with the same path in a list of nodes
        def find_node_by_path(nodes, node_a1):
            if allow_duplicates or a1.is_leaf or node_a1.is_leaf:
                return None
            else:
                for node in nodes:
                    if node.path == node_a1.path:
                        return node
                return None

        # Iterate through the nodes in a1
        for node_a1 in a1.twigs:
            # Check if there is an equivalent node in a0
            print(node_a1.is_leaf)
            existing_node_a0 = find_node_by_path(self.twigs, node_a1)
            if existing_node_a0 is not None:
                # Recursively merge the twigs of the two nodes
                existing_node_a0.merge_assemblies(node_a1, allow_duplicates)
            else:
                # If no corresponding node is found, add the node from a1 to a0
                self.add_child(node_a1)

    def add_by_index(self, name_list, data):
        # create branch

        branch_tree = Assembly_Tree("temp")
        last_branch = branch_tree
        for name in name_list:
            child = Assembly_Tree(name)
            last_branch.add_child(child)
            last_branch = child

        # add "real" data to the last branch
        data_node = Assembly_Tree(data)
        data_node.is_leaf = True
        last_branch.add_child(data_node)

        # merge this branch with the rest
        self.merge_assemblies(branch_tree, False)


def build_product_tree_0():
    # a0 branch
    root = Assembly_Tree("Oktoberfest")
    Schnitzel_Haus = Assembly_Tree("SchnitzelHaus")
    Bier = Assembly_Tree("Bier")
    Schnitzel = Assembly_Tree("Schnitzel")
    Sauce = Assembly_Tree("Sauce")
    Schnitzel.add_child(Sauce)
    Schnitzel_Haus.add_child(Bier)
    Schnitzel_Haus.add_child(Schnitzel)
    root.add_child(Schnitzel_Haus)

    # print(root.depth)
    # print(root.twigs[0].depth)
    return root


def build_product_tree_1():
    # a1 branch
    root = Assembly_Tree("Oktoberfest")
    Schnitzel_Haus = Assembly_Tree("SchnitzelHaus")
    Bier = Assembly_Tree("Bier")
    Bier2 = Assembly_Tree("Bier2")
    Schnitzel_Haus.add_child(Bier2)
    Schnitzel = Assembly_Tree("Schnitzel")
    Sauce = Assembly_Tree("Sauce")
    Sauce_White = Assembly_Tree("Sauce_White")
    Schnitzel.add_child(Sauce)
    Schnitzel.add_child(Sauce_White)
    Schnitzel_Haus.add_child(Bier)
    Schnitzel_Haus.add_child(Schnitzel)
    root.add_child(Schnitzel_Haus)
    # print(root.depth)
    # print(root.twigs[0].depth)
    return root


if __name__ == "__main__":
    a0 = build_product_tree_0()
    a0.print_tree()
    a1 = build_product_tree_1()
    a1.print_tree()
    a0.merge_assemblies(a1, True)
    a0.add_by_index(["SchnitzelHaus", "Schnitzel", "Sauce_White"], "_____Cream____")
    a0.add_by_index(["SchnitzelHaus", "Schnitzel", "Sauce_White"], "_____Cream____")
    a0.print_tree()
