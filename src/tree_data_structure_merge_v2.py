class Assembly_Node:
    def __init__(self, name, data, childs=None):
        self.name = name if name else "assembly_root"
        self.data = data  # data is empty if it is assembly and not an element
        self.children = childs if childs is not None else []
        self.parent = None

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    @property
    def full_name(self):
        return self.name + "_" + str(self.data)

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

        # Calculate the maximum depth by traversing children's subtrees
        return self._calculate_depth(self, depth)

    def _calculate_depth(self, node, depth):
        if not node.children:
            # If the node has no children, return the current depth
            return depth

        max_child_depth = depth
        for child in node.children:
            # Recursively calculate the depth for each child's subtree
            child_depth = self._calculate_depth(child, depth + 1)
            if child_depth > max_child_depth:
                max_child_depth = child_depth

        # Return the maximum depth among children's subtrees
        return max_child_depth

    def print_tree(self):
        prefix = "  " * self.level
        prefix = prefix + "|__ " if self.parent else ""
        print(prefix + self.name + " " + self.data)
        if self.children:
            for child in self.children:
                child.print_tree()

    def truncate_tree(self, value_to_remove):
        # Create a list to store nodes to remove
        nodes_to_remove = []

        # Traverse the tree to identify nodes with the given value
        def find_nodes_to_remove(node):
            if node.data == value_to_remove:
                nodes_to_remove.append(node)

            for child in node.children:
                find_nodes_to_remove(child)

        find_nodes_to_remove(self)

        # Remove the identified nodes and update parent-child relationships
        for node in nodes_to_remove:
            if node.parent:
                node.parent.children.remove(node)
                node.parent = None

    def merge_assemblies(self, _a1, allow_duplicate_data=True):
        # Helper function to find a node with the same name in a list of nodes
        def find_node_by_full_name(nodes, node_a1):
            if allow_duplicate_data:
                return None
            else:
                for node in nodes:
                    if allow_duplicate_data:
                        if node.name == node_a1.name:
                            return node
                    else:
                        if node.full_name == node_a1.full_name:
                            return node
                return None

        # for the very first one wrap it the node to another node
        #a1 = Assembly_Node("WARNING_TEMP_ASSEMBLY", _a1) if (_a1.level == 0) else _a1
        a1 = _a1
        print(a1.level)

        # Iterate through the nodes in a1
        for node_a1 in a1.children:
            # Check if there is an equivalent node in a0
            existing_node_a0 = find_node_by_full_name(self.children, node_a1)
            if existing_node_a0:
                # Recursively merge the children of the two nodes
                existing_node_a0.merge_assemblies(node_a1, allow_duplicate_data)
            else:
                # If no corresponding node is found, add the node from a1 to a0
                self.add_child(node_a1)


def add_by_index(node):
    # if the name is given as a level add the child to the assembly
    pass


def build_product_tree_0():
    # a0 assembly
    root = Assembly_Node("1", "Oktoberfest")
    laptop = Assembly_Node("2", "Schnitzel_Haus")
    keyboard = Assembly_Node("3", "Bier")
    screen = Assembly_Node("3", "Schnitzel")
    laptop.add_child(keyboard)
    laptop.add_child(screen)
    root.add_child(laptop)
    # print(root.depth)
    # print(root.children[0].depth)
    return root


def build_product_tree_1():
    # a1 assembly
    root = Assembly_Node("1", "Oktoberfest")
    laptop = Assembly_Node("2", "Schnitzel_Haus")
    keyboard = Assembly_Node("3", "Schnitzel")
    screen = Assembly_Node("3", "Wurstsalat")
    laptop.add_child(keyboard)
    laptop.add_child(screen)
    root.add_child(laptop)
    # print(root.depth)
    # print(root.children[0].depth)
    return root


if __name__ == "__main__":
    a0 = build_product_tree_0()
    # a0.print_tree()
    a1 = build_product_tree_1()
    a0.merge_assemblies(Assembly_Node("-1", "WARNING_TEMP_ASSEMBLY", [a1]), True)
    a0.print_tree()
    pass
