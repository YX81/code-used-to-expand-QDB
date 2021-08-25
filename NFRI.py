from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import pandas as pd
import numpy as np


class CrawlNfriData:
    def __init__(self, particle):
        """
        provide global variables for the class

        Parameters
        ----------
        self: the global variable to be defined
        particle: string
            the name of target element

        Returns
        -------
        global variable
        """
        self.particle = particle
        self.reactants = None
        self.products = None
        self.qdb_process = None
        self.url_list = []
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

    def open_web(self, url):
        """
        open the web page according to URL

        Parameters
        ----------
        self: defined in __init__ function
        url: string
            the link used to open related web

        Returns
        -------
        return the state of the currently simulated web page
        """
        driver = webdriver.Chrome()
        driver.get(url)
        driver.implicitly_wait(3)
        return driver

    def get_impact_list(self, driver, all_reaction):
        """
        get all the URLs used to store the data corresponding to each reaction type

        Parameters
        ----------
        self: defined in __init__ function
        driver: be used to simulate operations on a web page
        all_reaction: list
                     all the elements corresponding to the reaction type on the web

        Returns
        -------
        list
         all the URLs corresponding to the reaction type on the web
        """
        if not isinstance(all_reaction, list):
            raise ValueError('All_reaction should be a list.')

        n = len(all_reaction)
        id_list = []
        if n != 0:
            for reaction in all_reaction:
                id = reaction.get_attribute('id')
                id_list.append(id)

            for id in id_list:
                wait = WebDriverWait(driver, 3)
                element = wait.until(EC.element_to_be_clickable((By.ID, id)))
                driver.execute_script("arguments[0].click();", element)
                url = driver.current_url
                self.url_list.append(url)
                driver.back()
        else:
            self.url_list = []

    def decompose_nfri(self, formula):
        """
        get reactants and products from reaction formula

        Parameters
        ----------
        self: defined in __init__ function
        formula: string
                reaction formula crawled from NFRI database

        Returns
        -------
        string
         reactants in the formula
        string
         products in the formula
        """
        if not isinstance(formula, str):
            raise ValueError('Formula should be a string.')

        if re.search('->', formula) is not None:
            rea_position = re.search('->', formula).span()[0]
            reactant = formula[:rea_position]
            pro_position = re.search('->', formula).span()[1]
            product = formula[pro_position + 1:]
        else:
            reactant = formula
            product = ''
        self.reactants = reactant
        self.products = product

    def qdb_code(self, origin_process):
        """
        use QDB code to represent each reaction type

        Parameters
        ----------
        self: defined in __init__ function
        origin_process: string
                       reaction process crawled from NFRI database

        Returns
        -------
        string
         related QDB code
        """
        if not isinstance(origin_process, str):
            raise ValueError('Origin_process should be a string.')

        qdb_process = ''
        if 'Association Reaction' in origin_process:
            qdb_process = 'HIA'
        if 'Associative Ionization' in origin_process:
            qdb_process = 'HIA'
        if 'Associative Reaction' in origin_process:
            qdb_process = 'HAS'
        if 'Charge Transfer' in origin_process:
            qdb_process = 'HCX'
            if 'Dissociative' in origin_process:
                qdb_process = 'HDC'
        if 'Detachment' in origin_process:
            qdb_process = 'HED'
        if 'Excitation' in origin_process:
            qdb_process = 'HEX'
            if 'Quenching' in origin_process:
                qdb_process = 'HDX'
        if 'Partial Ionization' in origin_process or 'Single Ionization' in origin_process:
            qdb_process = 'HPI'
        if 'Particle Interchange Reaction' in origin_process or 'Reaction Reaction' in origin_process:
            qdb_process = 'HIR'
        if 'Total Recombination' in origin_process:
            qdb_process = 'HMM'
        if 'de-Excitation Excitation' in origin_process:
            qdb_process = 'HDX'
        if 'Dissociative Attachment' in origin_process:
            qdb_process = 'HET'
        if 'Radiative Reaction' in origin_process:
            qdb_process = 'HRA'
        self.qdb_process = qdb_process

    def get_information(self, x_unit, y_unit, numbers):
        """
        get all the basic information and reference information of all reaction in the table

        Parameters
        ----------
        self: defined in __init__ function
        x_unit: list
               the unit of temperature crawled from NFRI database
        y_unit: list
               the unit of rate coefficient crawled from NFRI database
        numbers: list
                elements corresponding to all records

        Returns
        -------
        17 lists
         each list used to store each information
        """
        if not isinstance(x_unit, list):
            raise ValueError('x_unit should be a list.')
        if not isinstance(y_unit, list):
            raise ValueError('y_unit should be a list.')
        if not isinstance(numbers, list):
            raise ValueError('Numbers should be a list.')

        for number in numbers:
            self.x_unit_l.append(x_unit[0])
            self.y_unit_l.append(y_unit[0])

            id = number.get_attribute('id')  # id[3:] is the number we want
            # get basic information
            b_url = 'https://dcpp.kfe.re.kr/search/popupViewBasic.do?plBiDataNum=' + id[3:]
            record_number = id[3:]
            self.record_number_l.append(record_number)
            driver_b = self.open_web(b_url)
            ref_number = driver_b.find_element_by_xpath('/html/body/div[2]/table/tbody/tr[1]/td/a/span').text
            self.ref_number_l.append(ref_number)
            # get data type
            data_type = driver_b.find_element_by_xpath('/html/body/div[2]/table/tbody/tr[7]/td').text
            self.data_type_l.append(data_type)
            # get reaction formula
            reaction_formula = driver_b.find_element_by_xpath('/html/body/div[2]/table/tbody/tr[8]/td').text
            self.reaction_formula_l.append(reaction_formula)
            # get reactants, products
            self.decompose_nfri(reaction_formula)
            self.reactants_l.append(self.reactants)
            self.products_l.append(self.products)
            # get reaction method
            collision_type = driver_b.find_element_by_xpath('/html/body/div[2]/table/tbody/tr[6]/td').text
            sub_process = driver_b.find_element_by_xpath('/html/body/div[2]/table/tbody/tr[5]/td').text
            collision_process = driver_b.find_element_by_xpath('/html/body/div[2]/table/tbody/tr[4]/td').text
            reaction_method = collision_type + ' ' + sub_process + ' ' + collision_process
            self.reaction_method_l.append(reaction_method)
            self.qdb_code(reaction_method)
            self.qdb_process_l.append(self.qdb_process)
            driver_b.close()

            # get reference information
            ref_url = 'https://dcpp.kfe.re.kr/search/popupViewArticle.do?plRaiArtclNum=' + ref_number
            driver_ref = self.open_web(ref_url)
            title = driver_ref.find_element_by_xpath('/html/body/div[2]/table/tbody/tr[2]/td').text
            author = driver_ref.find_element_by_xpath('/html/body/div[2]/table/tbody/tr[3]/td').text
            journal = driver_ref.find_element_by_xpath('/html/body/div[2]/table/tbody/tr[4]/td').text
            doi = driver_ref.find_element_by_xpath('/html/body/div[2]/table/tbody/tr[5]/td').text
            volume = driver_ref.find_element_by_xpath('/html/body/div[2]/table/tbody/tr[10]/td').text
            if driver_ref.find_element_by_xpath('/html/body/div[2]/table/tbody/tr[13]/td').text != '-':
                page = driver_ref.find_element_by_xpath(
                    '/html/body/div[2]/table/tbody/tr[12]/td').text + "-" + driver_ref.find_element_by_xpath(
                    '/html/body/div[2]/table/tbody/tr[13]/td').text
            else:
                page = driver_ref.find_element_by_xpath('/html/body/div[2]/table/tbody/tr[12]/td').text
            publish_year = driver_ref.find_element_by_xpath('/html/body/div[2]/table/tbody/tr[14]/td').text
            self.title_l.append(title)
            self.author_l.append(author)
            self.journal_l.append(journal)
            self.doi_l.append(doi)
            self.volume_l.append(volume)
            self.page_l.append(page)
            self.publish_year_l.append(publish_year)
            driver_ref.close()

    def get_actual_data(self, numbers):
        """
        get all the actual data of all reaction in the table

        Parameters
        ----------
        self: defined in __init__ function
        numbers: list
                elements corresponding to all records

        Returns
        -------
        4 lists
         each list used to store each data type
        """
        if not isinstance(numbers, list):
            raise ValueError('Numbers should be a list.')

        for number in numbers:
            # open numerical data page to get numerical data information
            id_number = number.get_attribute('id')  # id[3:] is the number we want
            data_url = 'https://dcpp.kfe.re.kr/search/popupView.do?type=numerical&plBiDataNum=' + id_number[3:]
            driver_data = self.open_web(data_url)
            count = len(driver_data.find_elements_by_xpath('//*[@id="tbody"]/tr'))
            for n in range(0, count):
                self.record_number_data.append(id_number[3:])
                x = driver_data.find_element_by_xpath('//*[@id="tbody"]/tr[' + str(n + 1) + ']/td[1]').text
                self.x_l.append(x)
                y = driver_data.find_element_by_xpath('//*[@id="tbody"]/tr[' + str(n + 1) + ']/td[2]').text
                self.y_l.append(y)
                y_max = driver_data.find_element_by_xpath('//*[@id="tbody"]/tr[' + str(n + 1) + ']/td[4]').text
                y_min = driver_data.find_element_by_xpath('//*[@id="tbody"]/tr[' + str(n + 1) + ']/td[5]').text
                if float(y_max) == float(y_min):
                    y_error = y_min
                else:
                    y_error = 'min:' + y_min + ',' + 'max:' + y_max
                self.y_error_l.append(y_error)
            driver_data.close()

    def get_information_and_data(self, driver, table_number):
        """
        organize all the information and data of each table I crawl into different dataframe

        Parameters
        ----------
        self: defined in __init__ function
        driver: be used to simulate operations on a web page
        table_number: int
                     the number of tables in each reaction type

        Returns
        -------
        dataframe
         store all the information in the table
        dataframe
         store all the actual data in the table
        """
        if not isinstance(table_number, int) or table_number <= 0:
            raise ValueError("Table_number should be integer and greater than 0.")

        # get x, y units
        x_axis = driver.find_elements_by_class_name('nv-axislabel')[0].text
        if re.search('[[]', x_axis) is not None:
            p1 = re.compile(r'[[](.*?)[]]', re.S)
            x_unit = re.findall(p1, x_axis)
        else:
            x_unit = ['K']
        y_axis = driver.find_elements_by_class_name('nv-axislabel')[1].text
        if re.search('[[]', y_axis) is not None:
            p2 = re.compile(r'[[](.*?)[]]', re.S)
            y_unit = re.findall(p2, y_axis)
        else:
            y_unit = ['cm^3/s']

        # get all number for all related reaction
        numbers = driver.find_elements_by_xpath('/html/body/div[3]/table[' + str(table_number) + ']/tbody/tr')
        self.get_information(x_unit, y_unit, numbers)
        self.get_actual_data(numbers)
        df_information = pd.DataFrame([self.record_number_l, self.reaction_formula_l, self.reaction_method_l,
                                       self.qdb_process_l, self.reactants_l, self.products_l, self.data_type_l,
                                       self.x_unit_l, self.y_unit_l, self.ref_number_l, self.doi_l, self.title_l,
                                       self.author_l, self.journal_l, self.volume_l, self.page_l, self.publish_year_l])
        df_information = df_information.T
        df_information.rename(columns={0: 'record_number', 1: 'reaction_formula', 2: 'reaction_method',
                                       3: 'QDB_process', 4: 'reactants', 5: 'products',
                                       6: 'Data_type', 7: 'temperature_unit', 8: 'rate_coefficient_unit',
                                       9: 'reference_number', 10: 'DOI',
                                       11: 'title', 12: 'author', 13: 'journal', 14: 'volume', 15: 'page',
                                       16: 'publish_year'},
                              inplace=True)
        df_data = pd.DataFrame([self.record_number_data, self.x_l, self.y_l, self.y_error_l])
        df_data = df_data.T
        df_data.rename(columns={0: 'record_number', 1: 'temperature', 2: 'rate_coefficient',
                                3: 'rate_coefficient_error'},
                       inplace=True)
        return df_information, df_data

    def get_all_data(self):
        """
        get all the information and actual data for a given particle

        Parameters
        ----------
        self: defined in __init__ function

        Returns
        -------
        dataframe
         store all the information for a given particle
        dataframe
         store all the actual data for a given particle
        """
        # open original database
        origin_url = 'https://dcpp.kfe.re.kr/index.do'
        driver = self.open_web(origin_url)

        # input some particle to get the related reaction
        driver.find_element_by_id('keyword').send_keys(self.particle)
        driver.implicitly_wait(3)
        driver.find_element_by_id('searchimg').click()
        driver.implicitly_wait(3)

        # find heavy particle impact in rate coefficient and get the url of each kind of reaction
        # judge if there is heavy particle impact
        if len(driver.find_elements_by_class_name('containerPlBiDataBranch')) != 0:
            id_number = driver.find_elements_by_class_name('containerPlBiDataBranch')[-1].get_attribute('id')
            if re.search(r'DB_03+', id_number) is not None and re.search(r'IC_03+', id_number) is not None:
                hpi_id = id_number
                all_reaction = driver.find_elements_by_xpath('//*[@id="' + hpi_id + '"]/a')
            else:
                all_reaction = []
            # A function to get id list, reaction name list and url list
            self.get_impact_list(driver, all_reaction)

        # get related information for each url
        if len(self.url_list) != 0:
            for url in self.url_list:
                # get the number of table in the url
                driver_url = self.open_web(url)
                table_tap = driver_url.find_elements_by_xpath('/html/body/div[3]/div[4]/a')
                number_table = len(table_tap)
                for m in range(1, number_table + 1):
                    # get dataframe for each table in each url
                    df_all_inf, df_all_data = self.get_information_and_data(driver_url, m)
                driver_url.close()
        else:
            df_all_inf = pd.DataFrame()
            df_all_data = pd.DataFrame()
        driver.close()
        return df_all_inf, df_all_data


if __name__ == '__main__':
    particle_list = list(np.array(pd.read_csv('element.csv')['0']))
    df_all_particle_inf = pd.DataFrame()
    df_all_particle_data = pd.DataFrame()
    for i in range(0, len(particle_list)):
        capture_data = CrawlNfriData(particle_list[i])
        df_particle_inf, df_particle_data = capture_data.get_all_data()
        df_all_particle_inf = df_all_particle_inf.append(df_particle_inf, ignore_index=True)
        df_all_particle_data = df_all_particle_data.append(df_particle_data, ignore_index=True)
    df_all_particle_inf.to_csv('NFRI_information.csv', index=False, encoding='utf_8_sig')
    df_all_particle_data.to_csv('NFRI_data.csv', index=False)
