import bpy

cmd = bpy.ops.object.empty_add

prop = cmd.get_rna_type().properties
print(prop)
print(dir(prop))

for c in prop:
    if c.is_hidden or c.is_readonly:
        continue
    print(c.identifier, c.type)
    print(dir(c))