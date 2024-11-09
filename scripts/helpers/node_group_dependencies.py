import bpy


def from_node(nodetree):
    return repr(nodetree).startswith("bpy.data.node_groups")

def separator():
    print('-----------------------------')

def get_childern(node):
    children = []
    
    
    if 'nodes' not in dir(node):
        return children
    
    for c in node.nodes:
        if c.bl_idname != 'GeometryNodeGroup':
            continue
        
        children.append(c)
        children += get_childern(c)
    
    return children

node_group_names = [n.name for n in bpy.data.node_groups]

for n in bpy.data.node_groups:
    print(f'"{n.name}" childern')

    
    separator()
    children = get_childern(n)
    for c in children:
        if c.node_tree is None:
            continue
        
        print(c.node_tree.name)

        
    separator()