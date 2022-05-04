import solid

import solid_state.query


def get_name(scad_obj):
    """
    Get the solid_state name of an object, if it has one.
    """
    if state := scad_obj.get_trait("solid_state"):
        return state["name"]

    return None


def _get_object_paths(scad_obj, query_path, path = (), results = None):
    if results is None:
        results = []

    term = query_path.terms[0]
    if(term.obj_name is None or term.obj_name == scad_obj.name):
        if(term.state_name is None or term.state_name == get_name(scad_obj)):
            if len(query_path.terms) == 1:
                results.append(path)

            else:
                query_path = solid_state.query.Path(terms=query_path.terms[1:])

    for i, child in enumerate(scad_obj.children):
        _get_object_paths(child, query_path, path + (i,), results)

    return results


def _get_paths_for_query(scad_obj, query_string):
    query = solid_state.query.parse(query_string)
    paths = []
    for query_path in query.paths:
        paths = [*paths, *_get_object_paths(scad_obj, query_path)]

    return paths


def get_objects(scad_obj, query):
    paths = _get_paths_for_query(scad_obj, query)

    objects = []
    for path in paths:
        tmp_obj = scad_obj
        for step in path:
            tmp_obj = tmp_obj.children[step]

        objects.append(tmp_obj)

    return objects


def get_object(scad_obj, query):
    """
    Get a single object with a given solid_state name. Throws an exception
    if a single match is not found.
    """
    objects = get_objects(scad_obj, query)

    num_objects = len(objects)
    if num_objects != 1:
        raise Exception(f"{num_objects} matches found for query when 1 was expected")

    return objects[0]


def get_attributes(scad_obj, query):
    """
    Get solid_state attributes of an object with the given name.
    """
    obj = get_object(scad_obj, query)
    return obj.get_trait("solid_state").get("attributes")


# TODO
# - DRY with get_objects
# - return reusable transformation functions not the actual objects
def get_transformations(scad_obj, query):
    """
    Get all transformations that were made after the named state.
    """
    paths = _get_paths_for_query(scad_obj, query)

    transformation_lookup = dict(
        color=solid.color,
        mirror=solid.mirror,
        rotate=solid.rotate,
        scale=solid.scale,
        translate=solid.translate,
    )

    results = []
    for path in paths:
        tmp_obj = scad_obj
        transformations = []
        for step in path:
            if tmp_obj.name in transformation_lookup:
                func = transformation_lookup[tmp_obj.name](**tmp_obj.params)
                transformations = [func, *transformations]

            tmp_obj = tmp_obj.children[step]

        results.append(transformations)

    return results
