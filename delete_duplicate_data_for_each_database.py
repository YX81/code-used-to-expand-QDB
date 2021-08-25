import pandas as pd
from decimal import Decimal


class DeleteDuplicateData:
    def __init__(self, inf_df, data_df):
        """
        provide global variables for the class

        Parameters
        ----------
        self: the global variable to be defined
        inf_df: dataframe
               dataframe including information of each database
        data_df: dataframe
                dataframe including data of each database

        Returns
        -------
        global variable
        """
        self.inf_df = inf_df
        self.data_df = data_df

    def delete_dup_inf(self):
        """
        a function to delete duplicate data in information dataframe

        Parameters
        ----------
        self: defined in __init__ function

        Returns
        -------
        dataframe
         includes all the information that is not repeated
        """
        non_dup_inf_df = self.inf_df.drop_duplicates(subset='record_number', keep='first')
        return non_dup_inf_df

    def delete_dup_data(self):
        """
        a function to delete duplicate data in data dataframe

        Parameters
        ----------
        self: defined in __init__ function

        Returns
        -------
        dataframe
         includes all the actual data that is not repeated
        """
        value_count = self.inf_df['record_number'].value_counts()
        dup_record_number = []
        for i in range(0, len(value_count)):
            if value_count.iloc[i] > 1:
                dup_record_number.append(value_count.index[i])
        new_data_df = self.data_df
        for k in range(0, len(dup_record_number)):
            # delete all data about this record number
            new_data_df = new_data_df[~new_data_df['record_number'].isin([dup_record_number[k]])]
            # for every record number, get the non dup data
            non_dup_df = self.data_df[self.data_df['record_number'] == dup_record_number[k]].drop_duplicates(
                subset='temperature', keep='first')
            new_data_df = new_data_df.append(non_dup_df, ignore_index=True)
        return new_data_df


if __name__ == '__main__':
    df_inf_nfri = pd.read_csv('NFRI_information.csv')
    df_data_nfri = pd.read_csv('NFRI_data.csv')
    df_inf_nifs = pd.read_csv('NIFS_information.csv')
    df_data_nifs = pd.read_csv('NIFS_data.csv')
    delete_dup_nfri = DeleteDuplicateData(df_inf_nfri, df_data_nfri)
    nondup_inf_nfri = delete_dup_nfri.delete_dup_inf()
    nondup_data_nfri = delete_dup_nfri.delete_dup_data()
    for d in range(0, len(nondup_data_nfri)):
        nondup_data_nfri['temperature'].iloc[d] = Decimal(nondup_data_nfri['temperature'].iloc[d]).normalize()
        nondup_data_nfri['rate_coefficient'].iloc[d] = Decimal(nondup_data_nfri['rate_coefficient'].iloc[d]).normalize()

    delete_dup_nifs = DeleteDuplicateData(df_inf_nifs, df_data_nifs)
    nondup_inf_nifs = delete_dup_nifs.delete_dup_inf()
    nondup_data_nifs = delete_dup_nifs.delete_dup_data()
    for d in range(0, len(nondup_data_nifs)):
        nondup_data_nifs['temperature'].iloc[d] = Decimal(nondup_data_nifs['temperature'].iloc[d]).normalize()
        nondup_data_nifs['rate_coefficient'].iloc[d] = Decimal(nondup_data_nifs['rate_coefficient'].iloc[d]).normalize()

    nondup_inf_nfri.to_csv('non_dup_nfri_information.csv', index=False, encoding='utf_8_sig')
    nondup_data_nfri.to_csv('non_dup_nfri_data.csv', index=False)
    nondup_inf_nifs.to_csv('non_dup_nifs_information.csv', index=False, encoding='utf_8_sig')
    nondup_data_nifs.to_csv('non_dup_nifs_data.csv', index=False)

