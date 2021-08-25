from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
import pandas as pd
import numpy as np
import ast


def get_nifs_elements(url):
    """
    get all the elements in the NIFS database

    Parameters
    ----------
    url: string
        a link used to open NIFS database

    Returns
    -------
    list
     includes all the elements
    """
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(3)
    # choose cmol
    driver.find_element_by_xpath('/html/body/center/table/tbody/tr[3]/td[3]/a[1]').click()
    driver.find_element_by_xpath('/html/body/div[1]').click()
    elements = driver.find_element_by_id('elementmasta').get_attribute('textContent')
    elements = ast.literal_eval(elements)
    element_l = []
    for j in range(0, len(elements)):
        element_l.append(elements[j]['el'])
    return element_l


def element(species):
    """
    delete charge in species for searching

    Parameters
    ----------
    species: string
            species in QDB

    Returns
    -------
    string
     species without charge
    """
    if not isinstance(species, str):
        raise ValueError('Species should be a string.')

    delete_plus = re.sub(r'[+]', '', species)
    ele = re.sub(r'-', '', delete_plus)
    return ele


if __name__ == '__main__':
    # get elements from NIFS database
    url_ori = 'https://dbshino.nifs.ac.jp/nifsdb/'
    nifs_element_list = get_nifs_elements(url_ori)
    # put element_list in csv file
    df_nifs_element = pd.DataFrame(nifs_element_list)
    df_nifs_element.to_csv('element_nifs.csv', index=False)

    # process species in the QDB
    species_list = list(np.array(pd.read_csv('qdb_species.csv')['ordinary_formula']))
    element_list = []
    for i in range(0, len(species_list)):
        element_list.append(element(species_list[i]))
    element_qdb_df = pd.DataFrame(element_list)
    element_qdb_df.to_csv('element_qdb.csv', index=False)
    # get all elements
    e_nifs = list(np.array(pd.read_csv('element_nifs.csv')['0']))
    e_qdb = list(np.array(pd.read_csv('element_qdb.csv')['0']))
    e_paper = list(np.array(pd.read_csv('element_paper.csv')['0']))
    e = e_nifs + e_paper + e_qdb
    element = sorted(list(set(e)))
    element_df = pd.DataFrame(element)
    element_df.to_csv('element.csv', index=False)
