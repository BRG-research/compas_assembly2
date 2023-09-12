"""
Assembly
Petras Vestartas
2021-10-01

# ==========================================================================
# Description
# ==========================================================================
The Assembly is a nested data structure of assemblies.

# ==========================================================================
# The minimal example
# ==========================================================================

NEVER DO THIS:
class Assembly:
    def __init__(self, assembly):
        self.assembly = assembly
        self.assemblies = []  # list<Assembly>

DO THIS INSTEAD BECAUSE ASSEMBLY MUST BE FINITE NOT RECURSIVE + IT CAN STORE PATH:
class AssemblyTree:
    def __init__(self, groupname_or_assembly):
        self.data = groupname_or_assembly  # can be a string or class<Assembly>
        self.parent = None
        self.childs = [] # list<Assembly_Tree>


# ==========================================================================
# What types are stored?
# ==========================================================================
The main property is called "data", it can be either:
a) group -> a string (indexing for the hierarch using text)
b) assembly -> class<assembly> (beams, plates, nodes, etc.)

# ==========================================================================
# How can the group hierarchy reperesented in one single class?
# ==========================================================================
It is represented by three propertes:
a) data -> group or class<assembly>
b) parent -> None or group
c) childs -> list<group or assembly or mix of both>

# ==========================================================================
# How new assemblies or groups are added?
# ==========================================================================
When a child assembly is added the parent is set to the data assembly.
def add_assembly(self, child):
    child.parent = self
    self.childs.append(child)

# ==========================================================================
# What the assembly is copied?
# ==========================================================================
One tree can have multiple references of the same object can exist in one assembly,
only one object exists in a memory, this is handled by UUID

# ==========================================================================
# What about links between elements?
# ==========================================================================

a) root assembly has links between elements (a graph), which can be empty
b) the root assembly stores all elements

+---+---+---+---+---+---+--MORE-DETAILS-BELOW--+---+---+---+---+---+---+---+

# ==========================================================================
# How assemblies are transformed?
# ==========================================================================
Transformation is performed on a data branch and its childs using methods:
a) transform, transformed
b) orient, oriented (for the most common operation)

# ==========================================================================
# How to vizualize a tree?
# ==========================================================================
def print_tree(self):
    prefix = "   " * self.level
    prefix = prefix + "|__ " if self.parent else ""
    print(prefix + self.path_str)
    if self.childs:
        for child in self.childs:
            child.print_tree()

# ==========================================================================
# How to know the level an object is nested at?
# ==========================================================================
@property
def level(self):
    level = 0
    p = self.parent
    while p:
        level = level + 1
        p = p.parent
    return level

# ==========================================================================
# How to know the depth an object is nested at?
# ==========================================================================
@property
def depth(self):
    # Initialize depth to 0 and start from the data node
    depth = 0
    current_node = self

    # Backtrack to the root parent while incrementing depth
    while current_node.parent:
        depth = depth + 1
        current_node = current_node.parent

    # Calculate the maximum depth by traversing childs's subtrees
    return self._calculate_depth(self, depth)


"""

import uuid


class Assembly:
    def __init__(self, data):
        self.uuid = uuid.uuid4()
        self.data = data

    def __str__(self):
        return f"Assembly with UUID: {self.uuid}, Data: {self.data}"

    def copy(self):
        copied_assembly = Assembly(self.data)
        copied_assembly.uuid = self.uuid
        return copied_assembly


class AssemblyTree:
    """AssemblyTree is a nested data structure of assemblies."""

    # ==========================================================================
    # Constructor and main body of the tree structureAssembly_Tree
    # ==========================================================================
    def __init__(self, groupname_or_assembly):
        self.data = groupname_or_assembly  # can be a string or class<assembly>
        self.parent = None
        self.childs = []
        self.uuid = uuid.uuid4()
        self.init_root_attributes()

    def add_child(self, child):
        child.parent = self
        child.transfer_root_attributes(self)
        self.childs.append(child)

    def __repr__(self):
        return self.name

    @property
    def name(self):
        if isinstance(self.data, str):
            return self.data
        else:
            return str(self.data)

    @property
    def group_or_assembly(self):
        return isinstance(self.data, str)

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
        # Initialize depth to 0 and start from the data node
        depth = 0
        current_node = self

        # Backtrack to the root parent while incrementing depth
        while current_node.parent:
            depth = depth + 1
            current_node = current_node.parent

        # Calculate the maximum depth by traversing childs's subtrees
        return self._calculate_depth(self, depth)

    def _calculate_depth(self, node, depth):
        if not node.childs:
            # If the node has no childs, return the data depth
            return depth

        max_child_depth = depth
        for child in node.childs:
            # Recursively calculate the depth for each child's subtree
            child_depth = self._calculate_depth(child, depth + 1)
            if child_depth > max_child_depth:
                max_child_depth = child_depth

        # Return the maximum depth among childs's subtrees
        return max_child_depth

    def print_tree(self):
        prefix = "   " * self.level
        prefix = prefix + "|__ " if self.parent else ""
        print(prefix + self.name)
        if self.childs:
            for child in self.childs:
                child.print_tree()

    # ==========================================================================
    # Functionality for the root assembly
    # ==========================================================================

    def init_root_attributes(self):
        if self.parent is None:
            self.graph = []
            self.all_assemblies = {}

    def remove_root_attributes(self):
        if self.parent is not None:
            del self.graph
            del self.all_assemblies

    def transfer_root_attributes(self, new_root):

        # --------------------------------------------------------------------------
        # if it was already the child it probably did not have any connectivity
        # --------------------------------------------------------------------------
        if self.parent is not None:
            return

        # --------------------------------------------------------------------------
        # update links
        # --------------------------------------------------------------------------
        n = len(self.graph)
        for pair in self.graph:
            new_root.graph.append(pair[0]+n, pair[1]+n)

        # --------------------------------------------------------------------------
        # update elements
        # --------------------------------------------------------------------------
        if (not self.group_or_assembly):
            self.all_assemblies[self.data.uuid] = self.data

        queue = [self]
        while queue:
            data = queue.pop(0)

            if (not self.group_or_assembly):
                self.all_assemblies[self.data.uuid] = self.data
            for child in data.childs:
                if (not child.group_or_assembly):
                    self.all_assemblies[child.data.uuid] = child.data
                else:
                    queue.append(child)

        # remove the attributes because they are not needed anymore
        self.remove_root_attributes()

    # ==========================================================================
    # Merging and adding assemblies
    # ==========================================================================

    def merge_assemblies(self, a1, allow_duplicate_assembly_trees=False, allow_duplicate_assemblies=True):
        # Helper function to find a node with the same name in a list of nodes
        def find_node_by_path(nodes, node_a1):
            if allow_duplicate_assembly_trees:  # or a1.group_or_assembly or node_a1.group_or_assembly
                return None
            else:

                if (allow_duplicate_assemblies):
                    if (node_a1.group_or_assembly is False):
                        return None
                
                for node in nodes:
                    if node.name == node_a1.name:
                        return node
                return None

        # Iterate through the nodes in a1
        for node_a1 in a1.childs:
            # Check if there is an equivalent node in a0
            existing_node_a0 = find_node_by_path(self.childs, node_a1)
            if existing_node_a0 is not None:
                # Recursively merge the childs of the two nodes
                existing_node_a0.merge_assemblies(node_a1, allow_duplicate_assembly_trees, allow_duplicate_assemblies)
            else:
                # If no corresponding node is found, add the node from a1 to a0
                self.add_child(node_a1)

    def add_by_index(self, name_list, data, allow_duplicate_assembly_trees=False, allow_duplicate_assemblies=True):
        # create data

        branch_tree = AssemblyTree("temp")
        last_branch = branch_tree
        for name in name_list:
            child = AssemblyTree(name)
            last_branch.add_child(child)
            last_branch = child

        # add "real" data to the last data
        last_branch.add_child(AssemblyTree(data))

        # merge this data with the rest
        self.merge_assemblies(branch_tree, False, True)

    # ==========================================================================
    # copy
    # ==========================================================================
    def copy(self):
        pass

    # ==========================================================================
    # transform
    # ==========================================================================
    def orient(self, orientation):
        pass

    def oriented(self, orientation):
        pass

    def transform(self, transformation):
        pass

    def transformed(self, transformation):
        pass


def build_product_tree_0():
    # a0 data
    root = AssemblyTree("Oktoberfest")
    Schnitzel_Haus = AssemblyTree("Restaurant The Taste of Berlin")
    Bier = AssemblyTree("Bier")
    Bier.add_child(AssemblyTree(Assembly("Water")))
    Bier.add_child(AssemblyTree(Assembly("Wheat malt")))
    Bier.add_child(AssemblyTree(Assembly("Noble hops")))
    Bier.add_child(AssemblyTree(Assembly("Wheat beer yeast")))

    Schnitzel = AssemblyTree("Schnitzel")
    Chicken = AssemblyTree(Assembly("Chicken"))
    Salt = AssemblyTree(Assembly("Salt"))
    Egg = AssemblyTree(Assembly("Egg"))
    Oil = AssemblyTree(Assembly("Oil"))
    Schnitzel.add_child(Chicken)
    Schnitzel.add_child(Salt)
    Schnitzel.add_child(Egg)
    Schnitzel.add_child(Oil)
    Schnitzel_Haus.add_child(Bier)
    Schnitzel_Haus.add_child(Schnitzel)
    root.add_child(Schnitzel_Haus)

    return root


def build_product_tree_1():
    # a1 data
    root = AssemblyTree("Oktoberfest")
    Schnitzel_Haus = AssemblyTree("Restaurant The Taste of Berlin")
    Bier = AssemblyTree("Bier")
    Bier.add_child(AssemblyTree(Assembly("Water")))
    Bier.add_child(AssemblyTree(Assembly("Pilsner malt")))
    Bier.add_child(AssemblyTree(Assembly("Saaz hops")))
    Bier.add_child(AssemblyTree(Assembly("Lager yeast")))

    Bier2 = AssemblyTree("Bier2")
    Schnitzel_Haus.add_child(Bier2)
    Schnitzel = AssemblyTree("Schnitzel")
    Veal = AssemblyTree(Assembly("Veal"))
    Salt = AssemblyTree(Assembly("Salt"))
    Egg = AssemblyTree(Assembly("Egg"))
    Butter = AssemblyTree(Assembly("Butter"))
    Lemon = AssemblyTree(Assembly("Lemon"))
    Schnitzel.add_child(Veal)
    Schnitzel.add_child(Salt)
    Schnitzel.add_child(Egg)
    Schnitzel.add_child(Egg)
    Schnitzel.add_child(Butter)
    Schnitzel.add_child(Lemon)
    Schnitzel_Haus.add_child(Bier)
    Schnitzel_Haus.add_child(Schnitzel)
    root.add_child(Schnitzel_Haus)
    # print(root.depth)
    # print(root.childs[0].depth)
    return root


if __name__ == "__main__":
    a0 = build_product_tree_0()
    # a0.print_tree()
    a1 = build_product_tree_1()
    # a1.print_tree()
    a0.merge_assemblies(a1)
    assembly = Assembly("_____Cream____")
    a0.add_by_index(["Restaurant The Taste of Berlin", "Schnitzel"], assembly)
    a0.add_by_index(["Restaurant The Taste of Berlin", "Schnitzel"], assembly)
    a0.print_tree()
