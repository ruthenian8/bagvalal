"""Binary search function for entry lookup"""


def index(elements, element):
    start = 0
    end = len(elements)
    if end == 0:
        raise KeyError("{} not in set".format(element))
    section = end - start
    pivot = start + section // 2
    pivot_element = elements[pivot]

    while section > 1:
        if pivot_element < element:
            start = pivot
        elif pivot_element > element:
            end = pivot
        else:
            return pivot
        section = end - start
        pivot = start + section // 2
        pivot_element = elements[pivot]

    if pivot_element == element:
        return pivot
    raise KeyError("{} not in set".format(element))
