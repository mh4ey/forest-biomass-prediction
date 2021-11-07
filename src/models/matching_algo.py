'''
Matching Algorithm2.0
Author : Jay Hombal
'''

import itertools
import time
import numpy as np
import pandas as pd
import logging
import os
from threading import Thread, Event
from multiprocessing import Process, Event  
from multiprocessing import synchronize, current_process  

class TreeMatching :

    
    PROCESSED_DATA_DIR = './data/processed/'
    # ground data file name
    plot1_processed_forest_ground_data_with_agb_file = 'plot1_processed_forest_ground_data_with_agb.csv'
    plot2_processed_forest_ground_data_with_agb_file = 'plot2_processed_forest_ground_data_with_agb.csv'

    # aerial data file name
    plot1_processed_aerial_data_file = 'plot1_processed_forest_aerial_data.csv'
    plot2_processed_aerial_data_file = 'plot2_processed_forest_aerial_data.csv'

    """
    init method or constructor 
    """
    def __init__(self, ground_data : pd.DataFrame, aerial_data: pd.DataFrame ):
        self.ground_data = ground_data
        self.aerial_data = aerial_data

    """
    Returns True if the tree from groun dataset is in the bounding box of an tree in aerial dataset
    """
    def isground_tree_inboundingbox(self, aerial_tree_Bbox_X1 : float,
            aerial_tree_Bbox_X2 : float,
            aerial_tree_Bbox_Y1 : float,
            aerial_tree_Bbox_Y2 : float,  
            ground_tree_X : float,
            ground_tree_Y : float) -> bool :
        if (ground_tree_X >= aerial_tree_Bbox_X1 and ground_tree_X <= aerial_tree_Bbox_X2)  \
            and (ground_tree_Y >= aerial_tree_Bbox_Y1 and ground_tree_Y <= aerial_tree_Bbox_Y2):
            return True
        else:
            return False

    """
    
    """
    def merge_aerial_ground_treedata(self, ar_row,  grnd_row) -> pd.DataFrame:
        """
        Returns matched ground data candidate trees merged with corresponding aerial tree 
        Args:
            ar_row ([type]): row from aerial dataset
            grnd_row ([type]): row from ground dataset

        Returns:
            pd.DataFrame: Returns a matched dataframe
        """
    
        candidate_matches = pd.DataFrame(columns =[
            'ground_data_tree_id', 'aerial_data_tree_id', 'stem_id','species', 'stem_diameter', 'agb','score', 'aerial_data_height',
            'area' , 'UTM_2018_X', 'UTM_2018_Y', 'left','bottom', 'right', 'top', 'tree_status', 'census_codes', 'adbin',  'gdbin'])
    

        candidate_matches = candidate_matches.append({'ground_data_tree_id' : grnd_row.tree_id,
                                        'aerial_data_tree_id' : ar_row.id,
                                        'stem_id' : grnd_row.stem_id,
                                        'species' : grnd_row.species,
                                        'stem_diameter' : grnd_row.stem_diameter,
                                        'agb': grnd_row.agb,
                                        'score': ar_row.score, #matched_tree['score'].iloc[0],
                                        'aerial_data_height': np.round(ar_row.height,7), #matched_tree['height'].iloc[0],
                                        'area': ar_row.area, #matched_tree['area'].iloc[0],
                                        'UTM_2018_X': grnd_row.UTM_2018_X,
                                        'UTM_2018_Y': grnd_row.UTM_2018_Y,
                                        'left': ar_row.left, #matched_tree['left'].iloc[0],
                                        'bottom': ar_row.bottom, # matched_tree['bottom'].iloc[0],
                                        'right': ar_row.right, #matched_tree['right'].iloc[0],
                                        'top': ar_row.top, #matched_tree['top'].iloc[0],
                                        'tree_status': grnd_row.tree_status,
                                        'census_codes': grnd_row.census_codes,
                                        'adbin': ar_row.adbin,
                                        'gdbin': grnd_row.gdbin,
                                       }, ignore_index=True)
        

        return candidate_matches
    

    def match_trees_byplot(self, aerial_data, ground_data, file_name):
        """
        Returns a Data frame matched trees for each plot

        Args:
            
            aerial_data ([type]): aerial trees for a given geo_index
            ground_data ([type]): ground trees for a given geo_index
            file_name ([type]): output_file name csv format 
            

        Returns:
            [type]: [description]
        """
        logger = logging.getLogger('__name__')
        name = current_process().name
        logger.info("Staring matching for " + name)

        #create and empty dataframe object
        matched_df = pd.DataFrame(columns =[
            'ground_data_tree_id', 'aerial_data_tree_id', 'stem_id','species', 'stem_diameter', 'agb', 'score', 'aerial_data_height', 
            'area' , 'UTM_2018_X', 'UTM_2018_Y', 'left','bottom', 'right', 'top',  'tree_status','census_codes', 'adbin','gdbin'])
        
        
        #1. Iterate through the aerial data set and match it with trees from ground dataset
        for ar_row in aerial_data.itertuples():

            candidate_matches = pd.DataFrame(columns =[
            'ground_data_tree_id', 'aerial_data_tree_id', 'stem_id','species', 'stem_diameter', 'agb', 'score', 'aerial_data_height',  
            'area' , 'UTM_2018_X', 'UTM_2018_Y', 'left','bottom', 'right', 'top',  'tree_status','census_codes', 'adbin','gdbin'])
        
            
            for grnd_row in ground_data.itertuples():

                is_tree_in_bb = self.isground_tree_inboundingbox(
                    ar_row.left, 
                    ar_row.right, 
                    ar_row.bottom,
                    ar_row.top,
                    grnd_row.UTM_2018_X,
                    grnd_row.UTM_2018_Y)
                
                if is_tree_in_bb:
                    # True if the bins match and False if the bins do not match
                    matchable_gdbins = [grnd_row.gdbin-1 if grnd_row.gdbin -1 > 0 else 0, \
                        grnd_row.gdbin,\
                        grnd_row.gdbin+1 if grnd_row.gdbin + 1 <= 5 else grnd_row.gdbin]
                  
                    is_bin_matching = True if ar_row.adbin in matchable_gdbins else False
                    # Create candidate matches - Merge the tree drata from aerial dataset with matched tree from ground dataset
                    if is_tree_in_bb == True and is_bin_matching == True:
                        candidate_row = self.merge_aerial_ground_treedata(ar_row=ar_row, grnd_row=grnd_row)
                        candidate_matches = candidate_matches.append(candidate_row)

            if len(candidate_matches) > 1 :
                matched_df = matched_df.append(candidate_matches[candidate_matches.agb == candidate_matches.agb.max()])
                tree_id = candidate_matches.nlargest(1, 'agb').ground_data_tree_id[0]

                # removing the matched tree from the ground dataset
                ground_data = ground_data[ground_data.tree_id != tree_id]
            elif len(candidate_matches) == 1:  
                
                matched_df = matched_df.append(candidate_matches)
                tree_id = candidate_matches.iloc[0,0]
                # removing the matched tree from the ground dataset
                ground_data = ground_data[ground_data.tree_id != tree_id]

        matched_df = matched_df.reset_index(drop=True)
        print(matched_df.shape)
        matched_df.to_csv(file_name, header=True, index=False)
        logger.info("Finished matching for " + name  + "and number of matching trees found :" + str( matched_df.shape[0]) )
        
    
def main():

        plot1_ground_data =pd.read_csv(TreeMatching.PROCESSED_DATA_DIR  + TreeMatching.plot1_processed_forest_ground_data_with_agb_file)
        plot2_ground_data =pd.read_csv(TreeMatching.PROCESSED_DATA_DIR  + TreeMatching.plot2_processed_forest_ground_data_with_agb_file)

        plot1_aerial_data=pd.read_csv(TreeMatching.PROCESSED_DATA_DIR  + TreeMatching.plot1_processed_aerial_data_file)
        plot2_aerial_data=pd.read_csv(TreeMatching.PROCESSED_DATA_DIR  + TreeMatching.plot2_processed_aerial_data_file)

        tree_matching1 = TreeMatching(plot1_ground_data,plot1_aerial_data)
        tree_matching2 = TreeMatching(plot2_ground_data,plot2_aerial_data)
        
        process1 = Process(name = 'Plot1-747000_4308000', target=tree_matching1.match_trees_byplot, 
                args=(plot1_aerial_data, \
                plot1_ground_data,\
                tree_matching1.PROCESSED_DATA_DIR +'plot1_matched_trees.csv'))  
        
        process2 = Process(name = 'Plot1-747000_4309000', target= tree_matching2.match_trees_byplot, 
                args=(plot2_aerial_data, \
                plot2_ground_data, \
                tree_matching2.PROCESSED_DATA_DIR +'plot2_matched_trees.csv' ))  

        # it is important to call join method after start method for each processes 
        process1.start() 
        process2.start()  
    
        process1.join()  
        process2.join()  
    
        plot1_matched_trees = pd.read_csv(TreeMatching.PROCESSED_DATA_DIR +'plot1_matched_trees.csv')
        plot2_matched_trees = pd.read_csv(TreeMatching.PROCESSED_DATA_DIR +'plot2_matched_trees.csv' )
        
        matched_trees = plot1_matched_trees.append(plot2_matched_trees)
        
        matched_trees.to_csv(TreeMatching.PROCESSED_DATA_DIR + 'all_matched_trees.csv', header=True, index=False)
        

# is the name is __main__ then call main()
if __name__ == "__main__":
    main()