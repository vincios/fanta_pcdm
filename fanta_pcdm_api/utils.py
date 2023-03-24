def str2bool(string: str):
    return string.lower() in ["true", "yes", "1", "si"]


def substitution_path(substitutions_as_tuples: list[tuple], target) -> list:
    """
    Returns a list of concorrenti, representing the substitution path of the given target

    For example, given the sostituzioni list
    ``[(C4. Ciro, C9. Ilaria), (C9. Ilaria, C13. Martina), (C13. Martina, None)]``
    the call ``substitution_path(subs_tuple2, ciro)`` will return ``[C9. Ilaria, C13. Martina, None]``
    :param substitutions_as_tuples: the sostituzioni list, as list of tuples instead of dictionaries
    :param target: the concorrente to give the substitution path
    :return: a list of concorrenti, representing the substitution path of the given concorrente
    """
    if not len(substitutions_as_tuples):
        return None

    first = substitutions_as_tuples[0]
    if first[0] and first[1] and target.id == first[0].id:
        r = substitution_path(substitutions_as_tuples[1:], first[1])
        return [first[1]] + r if isinstance(r, list) else [first[1]]
    elif first[0] and target.id == first[0].id and not first[1]:
        return [None]
    else:
        return substitution_path(substitutions_as_tuples[1:], target)
