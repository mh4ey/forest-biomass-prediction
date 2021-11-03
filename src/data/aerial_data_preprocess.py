import numpy as np
import pandas as pd
import uuid

class AerialDataProcessor:
    """
    Class for reading, processing, and writing data from the UCI
    Condition monitoring of hydraulic systems` dataset.
    """


    def __init__(self):
        
        self.aerial_data_usecols= ['left', 'bottom', 'right', 'top',
                        'score', 'height', 'area', 'geo_index']

        self.aerial_data = pd.DataFrame()

        self.aerial_data_processed_file = 'processed_forest_aerial_data.csv'
        

    def read_data(self, raw_data_path):
        """Read raw data into DataProcessor."""
        self.aerial_data =  pd.read_csv(raw_data_path, usecols= self.aerial_data_usecols)


    def process_data(self, stable=True):
        """Process raw data into useful files for model.
        Cleans the ground dataset
        """
        ground_data_geo_index = ['747000_4308000', '747000_4309000']
        bin_labels_5 = [1,2,3,4,5]
        ## Filter Aerial data matching the ground_data geo_index
        self.aerial_data = self.aerial_data[self.aerial_data['geo_index'].isin(ground_data_geo_index)]
        
        # create uuid
        ids = [uuid.uuid4() for _ in range(len(self.aerial_data.index))]
        self.aerial_data = self.aerial_data.assign(id =ids )

        
        self.aerial_data['adbin'] = pd.qcut(self.aerial_data['area'],
                              q=[0, .2, .4, .6, .8, 1],
                              labels=bin_labels_5)

        self.aerial_data.reset_index()

    def write_data(self, processed_data_path):
        """Write processed data to directory."""
        self.aerial_data.to_csv(processed_data_path + self.aerial_data_processed_file, header=True, index=False)
    
