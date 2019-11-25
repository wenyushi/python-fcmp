from __future__ import print_function, division, absolute_import, unicode_literals

EXPLICIT_FUNCTION = ['zeros']
__all__ = ['zeros']


def zeros(ret, shape):
    """
    Return a new array of given shape, filled with zeros.

    Parameters
    ----------
    ret : string
        Specifies the return variable of the function.
    shape : int or tuple of int
        Specifies the shape of the new array.

    Returns
    -------
    :class:`string`
    FCMP code to create the array.

    """
    if not isinstance(shape, list):
        shape = [shape]
    shape = [str(i) for i in shape]
    return 'array {0}[{1}]; do i = 1 to {1} by 1; {0}[i] = 0; end;'.format(ret, ' * '.join(shape))
