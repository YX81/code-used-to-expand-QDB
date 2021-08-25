import pytest
from element import *


def test_element():
    """
    test whether the parameter type is a string
    """
    with pytest.raises(ValueError) as e:
        element(3)
    assert e.match('Species should be a string.')

