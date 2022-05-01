def pipe(target, *fns):
    for fn in fns:
        target = fn(target)
    return target


def save_state(name, attributes = None):
    """
    Add solid_state metadata to an object.
    """
    if attributes is None:
        attributes = {}

    def _save_state(scad_obj):
        scad_obj.add_trait("solid_state", dict(name=name, attributes=attributes))
        return scad_obj
    return _save_state


def get_name(scad_obj):
    """
    Get the solid_state name of an object, if it has one.
    """
    if state := scad_obj.get_trait("solid_state"):
        return state["name"]

    return None


# TODO instead of building up list of objs directly,
# build up objs and any transformations found on the path to them.
# return like... {"objs": [], "transformations": []}
def get_objects(scad_obj, path, objs = None):
    """
    Get all objects with the given solid_state name.
    """
    if objs is None:
        objs = []

    path_parts = path.split(".")
    name = path_parts[0]

    if get_name(scad_obj) == name:
        if len(path_parts) == 1:
            objs.append(scad_obj)
            return objs

        path = ".".join(path_parts[1:])

    for child in scad_obj.children:
        objs = get_objects(child, path, objs)

    return objs


def get_object(scad_obj, name):
    """
    Get a single object with a given solid_state name. Throws an exception
    if a single match is not found.
    """
    objects = get_objects(scad_obj, name)
    num_objects = len(objects)
    if num_objects == 1:
        return objects[0]

    raise Exception(f"{num_objects} found when 1 was expected")


def get_attributes(scad_obj, name):
    """
    Get solid_state attributes of an object with the given name.
    """
    obj = get_object(scad_obj, name)
    return obj.get_trait("solid_state").get("attributes")


# TODO DRY with get_objects
def get_transformations(scad_obj, path, transformations = None):
    """
    Get all transformations that were made after the named state.
    """
    if transformations is None:
        transformations = []

    path_parts = path.split(".")
    name = path_parts[0]

    if get_name(scad_obj) == name:
        if len(path_parts) == 1:
            return transformations

        path = ".".join(path_parts[1:])

    transformation_types = {
        "color",
        "mirror",
        "rotate",
        "scale",
        "translate",
    }

    # TODO here and in test i think we can just check scad_obj.name
    if type(scad_obj).__name__ in transformation_types:
        transformations.insert(0, scad_obj)

    for child in scad_obj.children:
        transformations = get_transformations(child, path, transformations)
        if transformations is not None:
            return transformations

    return None
