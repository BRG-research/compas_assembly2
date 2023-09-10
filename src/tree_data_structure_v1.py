class TreeNode:
    def __init__(self, name, data):
        self.name = name if name else "assembly"
        self.data = data
        self.children = []
        self.parent = None

    def add_child(self, child):
        child.parent = self
        self.children.append(child)
    
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
        prefix = '  ' * self.level
        prefix = prefix + "|__ " if self.parent else ""
        print(prefix + self.name + " " + self.data)
        if self.children:
            for child in self.children:
                child.print_tree()

def build_product_tree():
    root = TreeNode("1", "Electronics")
    laptop = TreeNode("2", "Laptop")
    keyboard = TreeNode("3", "Keyboard")
    screen = TreeNode("3", "Screen")
    laptop.add_child(keyboard)
    laptop.add_child(screen)
    root.add_child(laptop)
    print(root.depth)
    print(root.children[0].depth)
    return root
      

if __name__ == '__main__':
    root = build_product_tree()
    root.print_tree()