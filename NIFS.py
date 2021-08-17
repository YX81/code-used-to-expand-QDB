from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
import pandas as pd
import numpy as np
import ast


class CrawlNifsData:
    def __init__(self, url, element):
        """
        provide global variables for the class

        Parameters
        ----------
        self: the global variable to be defined
        url: string
            the link used to open related web
        element: string
            the name of target element

        Returns
        -------
        global variable
        """
        self.url = url
        self.element = element
        self.reactants = None
        self.products = None
        self.qdb_process = None
        self.record_number_l = []
        self.ref_number_l = []
        self.data_type_l = []
        self.reaction_formula_l = []
        self.reactants_l = []
        self.products_l = []
        self.reaction_method_l = []
        self.qdb_process_l = []
        self.title_l = []
        self.author_l = []
        self.journal_l = []
        self.doi_l = []
        self.volume_l = []
        self.page_l = []
        self.publish_year_l = []
        self.x_unit_l = []
        self.y_unit_l = []
        self.record_number_data = []
        self.x_l = []
        self.y_l = []
        self.y_error_l = []

    def get_table_web(self, number=1):
        """
        open the web page of table which includes all relevant reactions of each element

        Parameters
        ----------
        self: defined in __init__ function
        number: int
               number in the state of species

        Returns
        -------
        return the state of the currently simulated web page
        """
        if not isinstance(number, int) or number <= 0:
            raise ValueError("Number should be integer and greater than 0.")

        driver = webdriver.Chrome()
        driver.get(self.url)
        driver.implicitly_wait(3)
        # choose CMOL
        driver.find_element_by_xpath('/html/body/center/table/tbody/tr[3]/td[3]/a[1]').click()
        # input element
        driver.find_element_by_xpath('//*[@id="basic_element_a1"]').send_keys(self.element)
        if self.element == 'H2':
            driver.find_element_by_xpath('//*[@id="basic_initial_excited_state_a"]').send_keys('v=' + str(number))
        # click rate coefficient
        driver.find_element_by_xpath('//*[@id="basic_data_type_rc"]').click()
        # search data
        driver.find_element_by_xpath('//*[@id="btn_search"]').click()
        return driver

    def qdb_code(self, origin_process):
        """
        use QDB code to represent each reaction type

        Parameters
        ----------
        self: defined in __init__ function
        origin_process: string
                       reaction process crawled from NIFS database

        Returns
        -------
        string
         related QDB code
        """
        if not isinstance(origin_process, str):
            raise ValueError('Origin_process should be a string.')

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
        self.qdb_process = qdb_process

    def decompose_nifs(self, formula, prod):
        """
        get reactants and products from reaction formula

        Parameters
        ----------
        self: defined in __init__ function
        formula: string
                reaction formula crawled from NIFS database
        prod: string
             products crawled from NIFS database

        Returns
        -------
        string
         reactants in the formula
        string
         products in the formula
        """
        if not isinstance(formula, str):
            raise ValueError('Formula should be a string.')
        if not isinstance(prod, str):
            raise ValueError('Parameter prod should be a string.')

        if re.search('-->', formula) is not None:
            rea_position = re.search('-->', formula).span()[0]
            reactant = formula[:rea_position]
        else:
            reactant = formula
        product = re.sub(';', r' + ', prod)
        self.reactants = reactant
        self.products = product

    def get_inf_data(self, driver):
        """
        get all the basic information and reference information of all reaction in the table

        Parameters
        ----------
        self: defined in __init__ function
        driver: be used to simulate operations on a web page

        Returns
        -------
        dataframe
         store all the information in the table
        """
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

            # the number of records
            number = len(driver.find_elements_by_xpath('//*[@id="list_form"]/ul'))
            # all useful information
            for i in range(1, number + 1):
                self.doi_l.append('')
                information_l = driver.find_element_by_xpath('//*[@id="list_form"]/ul[' + str(i) + ']').text.split('\n')
                self.record_number_l.append(re.findall(r'(?<== ).*$', information_l[0])[0])
                reaction_method = re.findall(r'(?<== ).*$', information_l[1])[0]
                self.reaction_method_l.append(reaction_method)
                self.data_type_l.append(re.findall(r'(?<== ).*$', information_l[2])[0])
                self.qdb_code(reaction_method)
                self.qdb_process_l.append(self.qdb_process)
                prod = re.findall(r'(?<== ).*$', information_l[5])[0]
                self.x_unit_l.append(re.findall(r'(?<== ).*$', information_l[6])[0])
                self.y_unit_l.append(re.findall(r'(?<== ).*$', information_l[7])[0])
                self.ref_number_l.append(re.findall(r'(?<== ).*$', information_l[8])[0])
                author = re.findall(r'(?<== ).*$', information_l[9])[0]
                rewrite_author = re.sub('[$]', ' ', author)
                self.author_l.append(rewrite_author)
                self.title_l.append(re.findall(r'(?<== ).*$', information_l[10])[0])
                self.journal_l.append(re.findall(r'(?<== ).*$', information_l[11])[0])
                self.volume_l.append(re.findall(r'(?<== ).*$', information_l[12])[0])
                self.page_l.append(re.findall(r'(?<== ).*$', information_l[13])[0])
                self.publish_year_l.append(re.findall(r'(?<== ).*$', information_l[14])[0])
                reaction_formula = re.findall(r'(?<== ).*$', information_l[15])[0]
                self.reaction_formula_l.append(reaction_formula)
                self.decompose_nifs(reaction_formula, prod)
                self.reactants_l.append(self.reactants)
                self.products_l.append(self.products)
            df_information = pd.DataFrame([self.record_number_l, self.reaction_formula_l, self.reaction_method_l,
                                           self.qdb_process_l, self.reactants_l, self.products_l, self.data_type_l,
                                           self.x_unit_l, self.y_unit_l, self.ref_number_l, self.doi_l,
                                           self.title_l, self.author_l, self.journal_l, self.volume_l, self.page_l,
                                           self.publish_year_l])
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

    def get_numerical_data(self, driver_data):
        """
        get all the actual data of all reaction in the table

        Parameters
        ----------
        self: defined in __init__ function
        driver_data: be used to simulate operations on a web page

        Returns
        -------
        dataframe
         store all the actual data in the table
        """
        if 'Found 0 Title(s)' != driver_data.find_element_by_xpath('/html/body/h3').text:
            # select numerical data
            driver_data.find_element_by_xpath('//*[@id="display_format_numeric"]').click()
            # display
            driver_data.find_element_by_xpath('//*[@id="btn_find_display"]').click()
            driver_data.find_element_by_xpath('//*[@id="display_write_vertical"]').click()
            driver_data.find_element_by_xpath('//*[@id="btn_num_display"]').click()

            number_data = len(driver_data.find_elements_by_xpath('//*[@id="display_form"]/ul'))
            for j in range(1, number_data + 1):
                data_l = driver_data.find_element_by_xpath(
                    '// *[ @ id = "display_form"] / ul[' + str(j) + ']').text.split(
                    '\n')
                all_data = driver_data.find_elements_by_xpath('/html/body/form/ul[' + str(j) + ']/ul/table/tbody/tr')
                for d in range(2, len(all_data) + 1):
                    record_number = re.findall(r'(?<==).*$', data_l[0])[0]
                    self.record_number_data.append(record_number)
                    x = driver_data.find_element_by_xpath(
                        '//*[@id="display_form"]/ul[' + str(j) + ']/ul/table/tbody/tr['
                        + str(d) + ']/td[1]').text
                    y = driver_data.find_element_by_xpath(
                        '//*[@id="display_form"]/ul[' + str(j) + ']/ul/table/tbody/tr['
                        + str(d) + ']/td[2]').text

                    self.x_l.append(x)
                    self.y_l.append(y)
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
                    self.y_error_l.append(y_error)
            df_data = pd.DataFrame([self.record_number_data, self.x_l, self.y_l, self.y_error_l])
            df_data = df_data.T
            df_data.rename(columns={0: 'record_number', 1: 'temperature', 2: 'rate_coefficient',
                                    3: 'rate_coefficient_error'},
                           inplace=True)
        else:
            df_data = pd.DataFrame()
        return df_data


if __name__ == '__main__':
    url_ori = 'https://dbshino.nifs.ac.jp/nifsdb/'
    element_list = list(np.array(pd.read_csv('element_nifs.csv')['0']))
    df_inf = pd.DataFrame()
    df_numerical_data = pd.DataFrame()
    for e in element_list:
        if e == 'H2':
            df_inf_e = pd.DataFrame()
            df_numerical_data_e = pd.DataFrame()
            # several different v
            for n in range(5, 14, 2):
                capture_data = CrawlNifsData(url_ori, e)
                driver_v = capture_data.get_table_web(n)
                df_inf_v = capture_data.get_inf_data(driver_v)
                df_inf_e = df_inf_e.append(df_inf_v, ignore_index=True)
                driver_v.close()
                driver_v_data = capture_data.get_table_web(n)
                df_numerical_data_v = capture_data.get_numerical_data(driver_v_data)
                df_numerical_data_e = df_numerical_data_e.append(df_numerical_data_v, ignore_index=True)
                driver_v_data.close()
        else:
            capture_data = CrawlNifsData(url_ori, e)
            driver_e = capture_data.get_table_web()
            df_inf_e = capture_data.get_inf_data(driver_e)
            driver_e.close()
            driver_e_data = capture_data.get_table_web()
            df_numerical_data_e = capture_data.get_numerical_data(driver_e_data)
            driver_e_data.close()
        df_inf = df_inf.append(df_inf_e, ignore_index=True)
        df_numerical_data = df_numerical_data.append(df_numerical_data_e, ignore_index=True)
    df_inf.to_csv('NIFS_information.csv', index=False, encoding='utf_8_sig')
    df_numerical_data.to_csv('NIFS_data.csv', index=False)