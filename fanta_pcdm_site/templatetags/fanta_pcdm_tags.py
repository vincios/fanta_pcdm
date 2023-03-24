from django import template

from fanta_pcdm_api.models import Concorrente
from fanta_pcdm_api.utils import substitution_path

register = template.Library()


@register.filter
def has_substitute_for(sostituzioni: list[dict[str, Concorrente]], concorrente: Concorrente) -> bool:
    """Returns True if the given concorrente has a substitute in the given substitutions list"""
    substitutions_as_tuple = [(s["fuori"], s["dentro"]) for s in sostituzioni]
    path = substitution_path(substitutions_as_tuple, concorrente)

    return path is not None and len(path) > 0


@register.filter
def substitution_path_for(sostituzioni: list[dict[str, Concorrente]], concorrente: Concorrente) -> list[Concorrente]:
    """Returns the substitution path for the given concorrente"""
    substitutions_as_tuple = [(s["fuori"], s["dentro"]) for s in sostituzioni]
    return substitution_path(substitutions_as_tuple, concorrente)


@register.filter
def substitute_for(sostituzioni: list[dict[str, Concorrente]], concorrente: Concorrente) -> Concorrente | None:
    """If the given concorrente is a substitute for ancother concorrente, returns the substituted concorrente"""
    # The idea is that if we reverse the substitution list, the substitution_path method will return the
    # substituted concorrente
    substitutions_as_tuple = list(reversed([(s["dentro"], s["fuori"]) for s in sostituzioni]))
    path = substitution_path(substitutions_as_tuple, concorrente)

    return path[-1] if path else None


@register.filter
def values_by_attr(lst: list[object] | list[dict], attr: str) -> list:
    """Aggregate all values of an attr of a list of objects"""
    res = []
    for element in lst:
        if element and isinstance(element, dict):
            res.append(element[attr])
        elif element and isinstance(element, object):
            res.append(getattr(element, attr))

    return res


@register.filter
def sum_lst(lst: list) -> int:
    """Equivalent of sum(lst)"""
    return sum(lst) if lst else 0


@register.filter
def attr(o: object | dict, name: str):
    """Equivalent of getattr(object, attribute) or dict.get"""
    if isinstance(o, dict):
        return o.get(name)
    elif isinstance(o, object):
        return getattr(o, name)
