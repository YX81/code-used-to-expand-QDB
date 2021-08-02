from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
import pandas as pd
import ast


def get_all_elements(url):
    driver = webdriver.Firefox()
    driver.get(url)
    driver.implicitly_wait(3)
    # choose cmol
    driver.find_element_by_xpath('/html/body/center/table/tbody/tr[3]/td[3]/a[1]').click()
    driver.find_element_by_xpath('/html/body/div[1]').click()
    elements = driver.find_element_by_id('elementmasta').get_attribute('textContent')
    elements = ast.literal_eval(elements)
    element_l = []
    for i in range(0, len(elements)):
        element_l.append(elements[i]['el'])
    return element_l


def get_table_web(url, element, number=1):
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(3)
    # choose cmol
    driver.find_element_by_xpath('/html/body/center/table/tbody/tr[3]/td[3]/a[1]').click()
    # input element
    driver.find_element_by_xpath('//*[@id="basic_element_a1"]').send_keys(element)
    if element == 'H2':
        driver.find_element_by_xpath('//*[@id="basic_initial_excited_state_a"]').send_keys('v=' + str(number))
    # click rate coefficient
    driver.find_element_by_xpath('//*[@id="basic_data_type_rc"]').click()
    # search data
    driver.find_element_by_xpath('//*[@id="btn_search"]').click()
    return driver


def qdb_code(origin_process):
    qdb_process = ''
    if 'charge transfer' in origin_process:
        qdb_process = 'HCX'
    if 'excitation' in origin_process or 'exciation' in origin_process:
        qdb_process = 'HEX'
        if 'vibration' in origin_process:
            qdb_process = ''
    if 'ionization' in origin_process:
        qdb_process = 'HDX'
    if 'mutual neutralization' in origin_process:
        qdb_process = 'HNE'
    if 'reactive' in origin_process:
        qdb_process = 'HIR'
        if 'vibration' in origin_process:
            qdb_process = ''
    return qdb_process


def decompose_nifs(formula, prod):
    if re.search('-->', formula) is not None:
        rea_position = re.search('-->', formula).span()[0]
        reactant = formula[:rea_position]
    else:
        reactant = formula
    product = re.sub(';', r' + ', prod)

    return reactant, product


def get_inf_data(driver):
    if 'Found 0 Title(s)' != driver.find_element_by_xpath('/html/body/h3').text:
        # select custom information
        driver.find_element_by_xpath('//*[@id="display_format_custom"]').click()
        # select all useful information
        for i in range(1, 9):
            for j in range(1, 5):
                if (i == 1 and j < 4) or (i == 2 and j == 1) or (i == 2 and j == 4) or (i == 3 and j == 4) or (
                        i == 5 and j > 1) or i == 6 or (i == 7 and j < 3) or (i == 8 and j == 3):
                    driver.find_element_by_xpath(
                        '/html/body/form/ul[2]/table/tbody/tr[' + str(i) + ']/td[' + str(j) + ']/input[2]').click()
        # display
        driver.find_element_by_xpath('//*[@id="btn_find_display"]').click()
        # store information into each list
        x_unit_l = []
        y_unit_l = []
        reaction_formula_l = []
        reaction_method_l = []
        title_l = []
        author_l = []
        journal_l = []
        volume_l = []
        page_l = []
        publish_year_l = []
        record_number_l = []
        reactants_l = []
        products_l = []
        ref_number_l = []
        qdb_process_l = []
        doi_l = []
        data_type_l =[]

        # the number of records
        number = len(driver.find_elements_by_xpath('//*[@id="list_form"]/ul'))
        # all useful information
        for i in range(1, number + 1):
            doi_l.append('')
            information_l = driver.find_element_by_xpath('//*[@id="list_form"]/ul[' + str(i) + ']').text.split('\n')
            record_number_l.append(re.findall(r'(?<== ).*$', information_l[0])[0])
            reaction_method = re.findall(r'(?<== ).*$', information_l[1])[0]
            reaction_method_l.append(reaction_method)
            data_type_l.append(re.findall(r'(?<== ).*$', information_l[2])[0])
            qdb_process = qdb_code(reaction_method)
            qdb_process_l.append(qdb_process)
            prod = re.findall(r'(?<== ).*$', information_l[5])[0]
            x_unit_l.append(re.findall(r'(?<== ).*$', information_l[6])[0])
            y_unit_l.append(re.findall(r'(?<== ).*$', information_l[7])[0])
            ref_number_l.append(re.findall(r'(?<== ).*$', information_l[8])[0])
            author = re.findall(r'(?<== ).*$', information_l[9])[0]
            rewrite_author = re.sub('[$]', ' ', author)
            author_l.append(rewrite_author)
            title_l.append(re.findall(r'(?<== ).*$', information_l[10])[0])
            journal_l.append(re.findall(r'(?<== ).*$', information_l[11])[0])
            volume_l.append(re.findall(r'(?<== ).*$', information_l[12])[0])
            page_l.append(re.findall(r'(?<== ).*$', information_l[13])[0])
            publish_year_l.append(re.findall(r'(?<== ).*$', information_l[14])[0])
            reaction_formula = re.findall(r'(?<== ).*$', information_l[15])[0]
            reaction_formula_l.append(reaction_formula)
            reactants, products = decompose_nifs(reaction_formula, prod)
            reactants_l.append(reactants)
            products_l.append(products)
        df_information = pd.DataFrame([record_number_l, reaction_formula_l, reaction_method_l, qdb_process_l,
                                       reactants_l, products_l, data_type_l, x_unit_l, y_unit_l, ref_number_l, doi_l,
                                       title_l, author_l, journal_l, volume_l, page_l, publish_year_l])
        df_information = df_information.T
        df_information.rename(columns={0: 'record_number', 1: 'reaction_formula', 2: 'reaction_method',
                                       3: 'QDB_process', 4: 'reactants', 5: 'products',
                                       6: 'Data_type', 7: 'temperature_unit', 8: 'rate_coefficient_unit',
                                       9: 'reference_number', 10: 'DOI',
                                       11: 'title', 12: 'author', 13: 'journal', 14: 'volume', 15: 'page',
                                       16: 'publish_year'},
                              inplace=True)
    else:
        df_information = pd.DataFrame()
    return df_information


def get_numerical_data(driver_data):
    if 'Found 0 Title(s)' != driver_data.find_element_by_xpath('/html/body/h3').text:
        # select numerical data
        driver_data.find_element_by_xpath('//*[@id="display_format_numeric"]').click()
        # display
        driver_data.find_element_by_xpath('//*[@id="btn_find_display"]').click()
        driver_data.find_element_by_xpath('//*[@id="display_write_vertical"]').click()
        driver_data.find_element_by_xpath('//*[@id="btn_num_display"]').click()

        x_l = []
        y_l = []
        y_error_l = []
        number_data = len(driver_data.find_elements_by_xpath('//*[@id="display_form"]/ul'))
        record_number_data = []
        for j in range(1, number_data + 1):
            data_l = driver_data.find_element_by_xpath('// *[ @ id = "display_form"] / ul[' + str(j) + ']').text.split(
                '\n')
            all_data = driver_data.find_elements_by_xpath('/html/body/form/ul[' + str(j) + ']/ul/table/tbody/tr')
            for d in range(2, len(all_data) + 1):
                record_number = re.findall(r'(?<==).*$', data_l[0])[0]
                record_number_data.append(record_number)
                x = driver_data.find_element_by_xpath('//*[@id="display_form"]/ul[' + str(j) + ']/ul/table/tbody/tr['
                                                      + str(d) + ']/td[1]').text
                y = driver_data.find_element_by_xpath('//*[@id="display_form"]/ul[' + str(j) + ']/ul/table/tbody/tr['
                                                      + str(d) + ']/td[2]').text

                x_l.append(x)
                y_l.append(y)
                y_error_plus = driver_data.find_element_by_xpath('//*[@id="display_form"]/ul['
                                                                 + str(j) + ']/ul/table/tbody/tr['
                                                                 + str(d) + ']/td[3]').text
                y_error_minus = driver_data.find_element_by_xpath('//*[@id="display_form"]/ul['
                                                                  + str(j) + ']/ul/table/tbody/tr['
                                                                  + str(d) + ']/td[4]').text
                if float(y_error_plus) == float(y_error_minus):
                    y_error = y_error_minus
                else:
                    y_error = 'min:' + y_error_minus + ',' + 'max:' + y_error_plus
                y_error_l.append(y_error)
        df_data = pd.DataFrame([record_number_data, x_l, y_l, y_error_l])
        df_data = df_data.T
        df_data.rename(columns={0: 'record_number', 1: 'temperature', 2: 'rate_coefficient',
                                3: 'rate_coefficient_error'},
                       inplace=True)
    else:
        df_data = pd.DataFrame()
    return df_data


if __name__ == '__main__':
    url_ori = 'https://dbshino.nifs.ac.jp/nifsdb/'
    element_list = get_all_elements(url_ori)
    # put element_list in csv file
    df_element = pd.DataFrame(element_list)
    df_element.to_csv('element_nifs.csv', index=False)
    df_inf = pd.DataFrame()
    df_numerical_data = pd.DataFrame()
    for e in element_list:
        if e == 'H2':
            df_inf_e = pd.DataFrame()
            df_numerical_data_e = pd.DataFrame()
            # several different v
            for n in range(5, 14, 2):
                driver_v = get_table_web(url_ori, e, n)
                df_inf_v = get_inf_data(driver_v)
                df_inf_e = df_inf_e.append(df_inf_v, ignore_index=True)
                driver_v.close()
                driver_v_data = get_table_web(url_ori, e, n)
                df_numerical_data_v = get_numerical_data(driver_v_data)
                df_numerical_data_e = df_numerical_data_e.append(df_numerical_data_v, ignore_index=True)
                driver_v_data.close()
        else:
            driver_e = get_table_web(url_ori, e)
            df_inf_e = get_inf_data(driver_e)
            driver_e.close()
            driver_e_data = get_table_web(url_ori, e)
            df_numerical_data_e = get_numerical_data(driver_e_data)
            driver_e_data.close()
        df_inf = df_inf.append(df_inf_e, ignore_index=True)
        df_numerical_data = df_numerical_data.append(df_numerical_data_e, ignore_index=True)
    df_inf.to_csv('NIFS_information.csv', index=False, encoding='utf_8_sig')
    df_numerical_data.to_csv('NIFS_data.csv', index=False)
