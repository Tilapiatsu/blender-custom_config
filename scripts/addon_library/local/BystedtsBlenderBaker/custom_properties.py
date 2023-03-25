import bpy
   
def silly_print(calling_function):
    print("DOUBLE OMG! Silly print from custom_properties! via " + calling_function)


def add(context, objects, property_name, value):
    '''
    Add custom property with [property_name] to object
    If custom property already exist, then add value to existing list or string
    replace existing value with [value] if it is not a list or a string

    objects (list) = objects to add custom property
    property_name (string) = name of custom property
    value (any data type) = value to add to custom property
    '''
    if not type(objects) == list:
        objects = [objects]
    if not type(value) == list:
        value = [value]

    for obj in objects:
        orig_value = get_value(context, obj, property_name)
        
        # Remove values that already exists in custom property
        trimmed_value = value.copy()
        for each in trimmed_value:
            if each in get_value(context, obj, property_name):
                trimmed_value.remove(each)

        # Avoid adding active object in custom property
        if obj in orig_value: 
            continue
        
        if property_exists(context, obj, property_name):
            if str(type(obj[property_name])) == "<class 'IDPropertyArray'>":
                obj[property_name] = obj[property_name].to_list() + trimmed_value
            elif type(obj[property_name]) is list or type(obj[property_name]) is str:
                obj[property_name] = obj[property_name] + trimmed_value
            else:
                obj[property_name] = trimmed_value
        else:
            obj[property_name] = trimmed_value

        
        

            


def property_exists(context, object, property_name):
    '''
    Check if property_name exists on object
    '''
    result = True
    try: 
        object[property_name] 
    except: 
        result = False
    return result

def exists_in_property(context, object, property_name, value):
    '''
    Check if value exists on objects property_name
    '''

    if not property_exists(context, object, property_name):
        return False

    property_val = object[property_name]

    if type(property_val) == list:
        result = value in property_val
    else: 
        result = value == property_val
    return result        
        
def get_value(context, objects, property_name):
    '''
    Get value(s) of property_name from all selected objects. 
    Multiple instances of same value is filtered out from the list 
    '''
    value_list = []
    if not type(objects) == list:
        objects = [objects]

    for obj in objects:
        if property_exists(context, obj, property_name):
            property_value = obj[property_name]

            # Make sure that property_value is a list
            if not type(property_value) == list:
                property_value = [property_value]

            # Add item to value_list unless it is already added
            for item in property_value:
                # Since we are checking multiple objects, we only want to add every item once
                if not item in value_list:
                    value_list.append(item)

    return value_list

def delete_property(context, objects, property_name):
    '''
    deletes custom property with name [property_name] from objects.
    '''
    if not type(objects) is list:
        objects = [objects]

    for object in objects:
        if property_exists(context, object, property_name):
            del object[property_name]