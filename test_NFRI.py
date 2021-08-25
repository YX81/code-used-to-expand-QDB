import pytest
from NFRI import CrawlNfriData


def test_get_impact_list():
    """
    test whether the parameter type is a list
    """
    particle = 'Br'
    capture_data = CrawlNfriData(particle)
    origin_url = 'https://dcpp.kfe.re.kr/index.do'
    driver = capture_data.open_web(origin_url)
    with pytest.raises(ValueError) as e:
        capture_data.get_impact_list(driver, '625f37d042aeec6b8a8469e735b7435c')
    assert e.match('All_reaction should be a list.')


def test_decompose_nfri():
    """
    test whether the parameter type is a string
    """
    particle = 'Br'
    capture_data = CrawlNfriData(particle)
    with pytest.raises(ValueError) as e:
        capture_data.decompose_nfri(3)
    assert e.match('Formula should be a string.')


def test_qdb_code():
    """
    test whether the parameter type is a string
    """
    particle = 'Br'
    capture_data = CrawlNfriData(particle)
    with pytest.raises(ValueError) as e:
        capture_data.qdb_code(5)
    assert e.match('Origin_process should be a string.')


def test_get_information():
    """
    test whether three parameters are lists
    """
    particle = 'Br'
    capture_data = CrawlNfriData(particle)
    with pytest.raises(ValueError) as e1:
        capture_data.get_information('K', ['cm^3/s'], ['6377d1cbbf48b912ad622b2962125088'])
    assert e1.match('x_unit should be a list.')
    with pytest.raises(ValueError) as e2:
        capture_data.get_information(['K'], 'cm^3/s', ['6377d1cbbf48b912ad622b2962125088'])
    assert e2.match('y_unit should be a list.')
    with pytest.raises(ValueError) as e3:
        capture_data.get_information(['K'], ['cm^3/s'], '6377d1cbbf48b912ad622b2962125088')
    assert e3.match('Numbers should be a list.')


def test_get_actual_data():
    """
    test whether the parameter type is a list
    """
    particle = 'Br'
    capture_data = CrawlNfriData(particle)
    with pytest.raises(ValueError) as e:
        capture_data.get_actual_data('6377d1cbbf48b912ad622b2962125088')
    assert e.match('Numbers should be a list.')


def test_get_information_and_data():
    """
    test whether the parameter is a integer and greater than 0
    """
    particle = 'Br'
    capture_data = CrawlNfriData(particle)
    url = 'https://dcpp.kfe.re.kr/search/list.do?plBiTopBranch=TB_01&plBiDataBranch=DB_03&plBiMainProc=MP_08&' \
          'plCpbiEleNum=A0093&keyword=Br&seltab=0&plBiImpClass=IC_03'
    driver = capture_data.open_web(url)
    with pytest.raises(ValueError) as e:
        capture_data.get_information_and_data(driver, -1)
    assert e.match('Table_number should be integer and greater than 0.')


