import re
import pandas as pd


class GetCompareDictionary:
    def __init__(self, df):
        """
        provide global variables for the class

        Parameters
        ----------
        self: the global variable to be defined
        df: dataframe
           used to provide the required information

        Returns
        -------
        global variable
        """
        self.df = df

    def decompose_list(self, r_number):
        """
        get reactants list and products list

        Parameters
        ----------
        self: defined in __init__ function
        r_number: int or string
                 record number in the NIFS database or NFRI database

        Returns
        -------
        list
         a list includes reactants of each reaction
        list
         a list includes products of each reaction
        """
        reactants = list(self.df[self.df['record_number'] == r_number]['reactants'])[0]
        products = list(self.df[self.df['record_number'] == r_number]['products'])[0]
        reactants_list = []
        products_list = []
        if re.search(r' [+]+', reactants) is not None:
            reactants = re.sub(r' [+]+', ';', reactants)
            if re.search(' ', reactants) is not None:
                reactants = re.sub(r' ', '', reactants)
            reactants = reactants.split(';')
            for r_number in reactants:
                reactants_list.append(r_number)
        else:
            if re.search(' ', reactants) is not None:
                reactants = re.sub(r' ', '', reactants)
            reactants_list.append(reactants)
        reactants_list = sorted(reactants_list)

        if type(products) == str:
            if re.search(r' [+]+', products) is not None:
                products = re.sub(r' [+]+', ';', products)
                if re.search(' ', products) is not None:
                    products = re.sub(r' ', '', products)
                products = products.split(';')
                for p in products:
                    products_list.append(p)
            else:
                if re.search(' ', products) is not None:
                    products = re.sub(r' ', '', products)
                products_list.append(products)
            products_list = sorted(products_list)
        else:
            products_list = []
        return reactants_list, products_list

    def get_dictionary(self):
        """
        get a dictionary for comparing reaction formula easily

        Parameters
        ----------
        self: defined in __init__ function

        Returns
        -------
        dictionary
         includes record number and reactants and products corresponding to each record number
        """
        dic = {}
        rn = list(self.df['record_number'])
        for n in rn:
            reactants_list, products_list = self.decompose_list(n)
            dic[n] = {'reactants': reactants_list, 'products': products_list}
        return dic


if __name__ == '__main__':
    nondup_inf_nfri = pd.read_csv('non_dup_nfri_information.csv')
    nondup_data_nfri = pd.read_csv('non_dup_nfri_data.csv')
    nondup_inf_nifs = pd.read_csv('non_dup_nifs_information.csv')
    nondup_data_nifs = pd.read_csv('non_dup_nifs_data.csv')

    # get the record number if they are the same reaction formula
    dup_rn_nfri = []
    dup_rn_nifs = []
    get_dic_nifs = GetCompareDictionary(nondup_inf_nifs)
    dict_nifs = get_dic_nifs.get_dictionary()
    get_dic_nfri = GetCompareDictionary(nondup_inf_nfri)
    dict_nfri = get_dic_nfri.get_dictionary()
    for k1 in dict_nifs.keys():
        for k2 in dict_nfri.keys():
            if dict_nfri[k2]['reactants'] == dict_nifs[k1]['reactants'] and dict_nfri[k2]['products'] == \
                    dict_nifs[k1]['products']:
                # check if they have the same data
                data_nfri = nondup_data_nfri[nondup_data_nfri['record_number'] == k2]
                data_nfri = data_nfri.sort_values(by=['temperature'], ascending=True)
                data_nifs = nondup_data_nifs[nondup_data_nifs['record_number'] == k1]
                data_nifs = data_nifs.sort_values(by=['temperature'], ascending=True)
                if list(data_nifs['temperature']) == list(data_nfri['temperature']) and \
                        list(data_nifs['rate_coefficient']) == list(data_nfri['rate_coefficient']):
                    dup_rn_nifs.append(k1)
                    dup_rn_nfri.append(k2)
    # delete all information and data in nfri according to related record number
    for j in range(0, len(dup_rn_nfri)):
        # compare year
        nfri_publish_year = int(nondup_inf_nfri[nondup_inf_nfri['record_number'] == dup_rn_nfri[j]]['publish_year'])
        nifs_publish_year = int(nondup_inf_nifs[nondup_inf_nifs['record_number'] == dup_rn_nifs[j]]['publish_year'])
        if nfri_publish_year > nifs_publish_year:
            nondup_inf_nfri = nondup_inf_nfri[~nondup_inf_nfri['record_number'].isin([dup_rn_nfri[j]])]
            nondup_data_nfri = nondup_data_nfri[~nondup_data_nfri['record_number'].isin([dup_rn_nfri[j]])]
        else:
            nondup_inf_nifs = nondup_inf_nifs[~nondup_inf_nifs['record_number'].isin([dup_rn_nifs[j]])]
            nondup_data_nifs = nondup_data_nifs[~nondup_data_nifs['record_number'].isin([dup_rn_nifs[j]])]
    # combine all the data
    all_inf = nondup_inf_nifs.append(nondup_inf_nfri, ignore_index=True)
    all_data = nondup_data_nifs.append(nondup_data_nfri, ignore_index=True)

    # add data source
    rn_inf = list(all_inf['record_number'])
    inf_data_source = []
    for r in rn_inf:
        if r in list(nondup_inf_nfri['record_number']) and r not in dup_rn_nfri:
            inf_data_source.append('NFRI')
        elif r in list(nondup_inf_nifs['record_number']) and r not in dup_rn_nifs:
            inf_data_source.append('NIFS')
        else:
            inf_data_source.append('BOTH')
    all_inf['data_source'] = inf_data_source

    rn_data = list(all_data['record_number'])
    actual_data_source = []
    for r in rn_data:
        if r in list(nondup_inf_nfri['record_number']) and r not in dup_rn_nfri:
            actual_data_source.append('NFRI')
        elif r in list(nondup_inf_nifs['record_number']) and r not in dup_rn_nifs:
            actual_data_source.append('NIFS')
        else:
            actual_data_source.append('BOTH')
    all_data['data_source'] = actual_data_source

    all_inf.to_csv('information.csv', index=False, encoding='utf_8_sig')
    all_data.to_csv('data.csv', index=False)
