# code-used-to-expand-QDB
Some codes used to capture data and expand QDB
* element.py: some codes used to get all the elements
* element_nifs.csv: elements captured from NIFS database
* element_paper.csv: elements in the previous paper
* qdb_species: species in QDB used to get elements in QDB
* element_qdb.csv: elements in the QDB
* element.csv: All the elements were got by using code in element.py and three CSV files mentioned before.
* NFRI.py: some codes used to capture all the information and numerical data of rate coeficients of heavy-particle reactions in NFRI database
* NFRI_data.csv: including all the numerical data captured from NFRI database by using codes in NFRI.py
* NFRI_information.csv: including all the basic information and reference information captured from NFRI databaseby by using codes in NFRI.py
* NIFS.py: some codes used to capture all the information and numerical data of rate coeficients of heavy-particle reactions in NIFS database
* NIFS_data.csv: including all the numerical data captured from NIFS database by using codes in NIFS.py
* NIFS_information.csv: including all the basic information and reference information captured from NIFS database by using codes in NIFS.py
* delete_duplicate_data_for_each_database.py: some codes used to delete duplicates in NFRI_data.csv, NFRI_information.csv, NIFS_data.csv, NIFS_information.csv respectively
* non_dup_nfri_data.csv, non_dup_nfri_information.csv, non_dup_nifs_data.csv, non_dup_nifs_information.csv: Files do not contain duplicates by running codes in delete_duplicate_data_for_each_database.py and four CSV files including NFRI_data.csv, NFRI_information.csv, NIFS_data.csv, NIFS_information.csv.
* combine_all_data.py: some codes used to delete duplicates in the two databases, combine all information and data and add data sources.
* data.csv: all numerical data got by running combine_all_data.py
* information.csv: all basic information and reference information got by running combine_all_data.py
* test_element: pytest used to test codes in element.py
* test_NFRI: pytest used to test codes in NFRI.py
* test_NIFS: pytest used to test codes in NIFS.py
