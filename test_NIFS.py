import pytest
from NIFS import CrawlNifsData


def test_get_table_web():
    """
    test whether the parameter is a integer and greater than 0
    """
    url = 'https://dbshino.nifs.ac.jp/nifsdb/'
    element = 'Br'
    capture_data = CrawlNifsData(url, element)
    with pytest.raises(ValueError) as e:
        capture_data.get_table_web(0)
    assert e.match('Number should be integer and greater than 0.')


def test_qdb_code():
    """
    test whether the parameter type is a string
    """
    url = 'https://dbshino.nifs.ac.jp/nifsdb/'
    element = 'Br'
    capture_data = CrawlNifsData(url, element)
    with pytest.raises(ValueError) as e:
        capture_data.qdb_code(5)
    assert e.match('Origin_process should be a string.')


def test_decompose_nifs():
    """
    test whether two parameters are string
    """
    url = 'https://dbshino.nifs.ac.jp/nifsdb/'
    element = 'Br'
    capture_data = CrawlNifsData(url, element)
    with pytest.raises(ValueError) as e1:
        capture_data.decompose_nifs('H2 (v=5) + H2 (v=11) --> H', 7)
    assert e1.match('Parameter prod should be a string.')
    with pytest.raises(ValueError) as e2:
        capture_data.decompose_nifs(7, 'H')
    assert e2.match('Formula should be a string.')


