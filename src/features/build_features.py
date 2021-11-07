import numpy as np
import pandas as pd


class FeatureBuilder:
    """
    Class for reading, processing, and writing data from the UCI
    Condition monitoring of hydraulic systems` dataset.
    """


    def __init__(self):
        
        # ground data file name
        self.ground_data_file = 'interim_forest_ground_data_with_agb.csv'
        self.ground_data_processed_file = 'processed_forest_ground_data_with_agb.csv'

        self.ground_interim_data = pd.DataFrame()

    def read_data(self, raw_data_path):
        """Read raw data into DataProcessor."""
        self.ground_interim_data =  pd.read_csv(raw_data_path)


    def process_data(self, stable=True):
        """
        Build new features
        """
        # methods to add geo_index column
        def subX(x):
            return str(x)[0:3] +'000'
        def subY(y):
            return str(y)[0:4] +'000'
        
        # assign geo_index column
        self.ground_interim_data  = self.ground_interim_data .assign(geo_index = self.ground_interim_data ['UTM_2018_X'].apply(subX) + '_' + self.ground_interim_data ['UTM_2018_Y'].apply(subY))

        #round values assign UTM_2018_X and UTM_2018_Y columns - UTM Coordinates from fround dataset
        self.ground_interim_data ['UTM_2018_X'] = round(self.ground_interim_data ['UTM_2018_X'],1)
        self.ground_interim_data ['UTM_2018_Y'] = round(self.ground_interim_data ['UTM_2018_Y'],1)
        
        # role up multiple stems per tree to one tree
        self.ground_interim_data ['total_agb'] = self.ground_interim_data .groupby('tree_id').agb.transform('sum')
        self.ground_interim_data  = self.ground_interim_data .drop_duplicates(subset=['tree_id'])
        self.ground_interim_data .drop('agb', axis=1, inplace=True)
        self.ground_interim_data .rename(columns = {'total_agb':'agb'}, inplace = True)

        # add bin number
        bin_labels_5 = [1,2,3,4,5]
        self.ground_interim_data['gdbin'] = pd.qcut(self.ground_interim_data['agb'],
                              q=[0, .2, .4, .6, .8, 1],
                              labels=bin_labels_5)

    def write_data(self, processed_data_path):
        """Write processed data to directory."""
        plot1 = self.ground_interim_data[self.ground_interim_data['geo_index'] == '747000_4308000']
        plot2 = self.ground_interim_data[self.ground_interim_data['geo_index'] == '747000_4309000']
        plot1.to_csv(processed_data_path + 'plot1_' + self.ground_data_processed_file , header=True, index=False)
        plot2.to_csv(processed_data_path + 'plot2_' + self.ground_data_processed_file , header=True, index=False)
    