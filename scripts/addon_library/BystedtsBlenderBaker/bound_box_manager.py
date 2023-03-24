import bpy
import mathutils
import copy


def get_cubic_bounding_box():
    '''
    Return the bounding box of a 2 unit dimensional cube
    '''
    bb = []
    bb.append(mathutils.Vector([-1.0000, -1.0000, -1.0000]))
    bb.append(mathutils.Vector([-1.0000, -1.0000, 1.0000]))
    bb.append(mathutils.Vector([-1.0000, 1.0000, 1.0000]))
    bb.append(mathutils.Vector([-1.0000, 1.0000, -1.0000]))
    bb.append(mathutils.Vector([1.0000, -1.0000, -1.0000]))
    bb.append(mathutils.Vector([1.0000, -1.0000, 1.0000]))
    bb.append(mathutils.Vector([1.0000, 1.0000, 1.0000]))
    bb.append(mathutils.Vector([1.0000, 1.0000, -1.0000]))
    
    return bb

def transform_vector_by_rotation(vector, matrix):
    
    m = copy.copy(matrix)
    # Remove location from matrix 
    for i in range (0,3):
        m[i][3] = 0
    
    return m @ vector

def get_bounding_box(object, world_matrix = True):
    '''
    Returns bounding box of object. Returns points in world space if world_matrix = True
    '''
    bb = []
    
    # Get vector per bounding box point
    for i in range(0,8):
        v = mathutils.Vector(object.bound_box[i])
        if world_matrix:
            v = object.matrix_world @ v
        bb.append(v)
        
    return bb

def get_oriented_cubic_bounding_box(object):
    '''
    Return the bounding box of a 2 unit dimensional cube that is
    oriented to the objects world matrix, but in origo
    '''
    bb = get_cubic_bounding_box()
    
    for i in range(0,8):
        bb[i] = transform_vector_by_rotation(bb[i], object.matrix_world)

    return bb

def get_index_to_closest_bounding_box_point(vector, bounding_box):
    '''
    Return the index of the closest point on the bounding box
    ''' 
    bb = bounding_box
    min_distance = 1000000000000000
    closest_index = -1
        
    for i in range(0,8):
        distance = (vector-bb[i]).length

        if distance < min_distance:
            min_distance = distance
            closest_index = i
            
    return closest_index

def get_reordered_bounding_box_by_source_object(source_object, reorder_bb_object, world_matrix = True):
    '''
    Returns a bounding box of reorder_bb_object, that is reordered to be as close as possible 
    to source_object in terms of it's orientation etc. This eliminates issues of rotation and 
    inverted scale
    '''
    source_cubic_bb = get_oriented_cubic_bounding_box(source_object)
    reorder_cubic_bb = get_oriented_cubic_bounding_box(reorder_bb_object)    
    reorder_world_matrix_bb = get_bounding_box(reorder_bb_object, world_matrix)
    reordered_bb = []
        
    #test_print_bb(source_cubic_bb, "source_cubic_bb")
    #test_print_bb(reorder_cubic_bb, "reorder_cubic_bb - oriented")
    
    for i in range(0,8):
        j = get_index_to_closest_bounding_box_point(source_cubic_bb[i], reorder_cubic_bb)
        reordered_bb.append(reorder_world_matrix_bb[j])
    
    return reordered_bb


def get_bounding_box_difference_distance(source_object, compare_object, world_matrix = True):
    '''
    returns the difference between two objects bounding boxes by comparing the closest points between each bounding box
    '''
        
    # Get vector per bounding box point
    source_bb = get_bounding_box(source_object, world_matrix)
    compare_bb = get_reordered_bounding_box_by_source_object(source_object, compare_object, world_matrix)
    bb_difference = 0

    test_print_bb(source_bb, source_object.name)
    test_print_bb(compare_bb, compare_object.name)
        

    for i in range(0,8):
        bb_difference += (source_bb[i]-compare_bb[i]).length

    return bb_difference


def test_print_bb(bb, additional_string = ""):
    
    print("\n")
    print(additional_string)
    
    for i in bb:
        print(str(i))