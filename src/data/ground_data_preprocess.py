import numpy as np
import pandas as pd


class GroundDataProcessor:
    """
    Class for reading, processing, and writing data from the UCI
    Condition monitoring of hydraulic systems` dataset.
    """


    def __init__(self):
        
        # ground data file name
        #self.ground_data_file = 'ground_source_data.csv'
        self.ground_data_clean_file = 'interim_forest_ground_data_with_agb.csv'
       
        # ground data new column names
        self.ground_data_column_names = {
            'treeID' : 'tree_id', 
            'stemID': 'stem_id', 
            'Genus' : 'genus',
            'sp': 'species',
            'agb': 'agb',
            'dbh': 'stem_diameter', 
            'codes': 'census_codes', 
            'status' : 'tree_status', 
            'NAD83_X' : 'UTM_2018_X', 
            'NAD83_Y': 'UTM_2018_Y', 
            'lat': 'latitude', 
            'lon': 'longitude'
        }

        self.ground_data_tree_or_stem_status_codes = {
            'A' : 'alternate POM (point of measure differnt than 1.3)',
            'B' : 'stem broken above 1.3m',
            'C' : 'dead above 1.3m',
            'F' : 'inside deer fence',
            'G' : 'ID to Genius certian',
            'I' : 'stem irrigular where measured',
            'J' : 'bent',
            'L' : 'leaning stem',
            'M' : 'Multiple stem plant',
            'X' : 'stem broken below 1.3 m',
            'P' : 'prostrate stem (allmost parallel to the ground)',
            'S' : 'secondary stem',
            'TR' : 'tag removed',
            'WR' : 'wire removed',
            'DS' : 'dead stem standing',
            'DC' : 'dead stem fallen',
            'DT' : 'dead only tag found',
            'DN' : 'presumed dead no tag or stem',
            'main' : 'main stem',  
        }

        self.ground_data_dead_tree_or_stem_census_codes = ['B','C', 'X' 'DS*', 'DC','DT', 'DN']

 
        self.ground_data = pd.DataFrame()

    def read_data(self, raw_data_path):
        """Read raw data into DataProcessor."""
        self.ground_data =  pd.read_csv(raw_data_path, usecols= self.ground_data_column_names)


    def process_data(self, stable=True):
        """Process raw data into useful files for model.
        Cleans the ground dataset
        """
        # methods to add geo_index column
        def subX(x):
            return str(x)[0:3] +'000'
        def subY(y):
            return str(y)[0:4] +'000'
        

        # sub select only columns we are interested in
        self.ground_data =  self.ground_data.rename(columns=self.ground_data_column_names)
        
        #assign geo_index
        self.ground_data = self.ground_data.assign(geo_index = self.ground_data['UTM_2018_X'].apply(subX) + '_' + self.ground_data['UTM_2018_Y'].apply(subY))

        # impute the missing tree status codes, if the data is missing we are assuming the tree to be main stem
        self.ground_data['census_codes']= np.where(self.ground_data['census_codes'].isnull(), 'main', self.ground_data['census_codes'])

        #convert the discrete value columns to category type
        self.ground_data[['tree_status']].assign(DFstatus=self.ground_data['tree_status'].astype('category'))
        self.ground_data[['species']].assign(sp = self.ground_data['species'].astype('category'))
        self.ground_data[['census_codes']].assign(status = self.ground_data['census_codes'].astype('category'))

        # retain only those rows which have the dbh value
        self.ground_data = self.ground_data[self.ground_data['stem_diameter'].notna()]
        
        # drop dead and broken trees
        self.ground_data = self.ground_data[~self.ground_data['census_codes'].isin(self.ground_data_dead_tree_or_stem_census_codes)]
        self.ground_data['census_codes'].isin(self.ground_data_dead_tree_or_stem_census_codes).value_counts()

        # drop bottom 25% trees based on agb
        # ground_data.stem_diameter.describe(percentiles=[.25]).reset_index() = 14.0
        self.ground_data = self.ground_data[self.ground_data['stem_diameter'] > 14.0]

        #filterout all trees having agb greater than 6000
        self.ground_data = self.ground_data[self.ground_data['agb'] <= 6000.0]

    def write_data(self, processed_data_path):
        """Write processed data to directory."""

        self.ground_data.to_csv(processed_data_path + self.ground_data_clean_file, header=True, index=False)

