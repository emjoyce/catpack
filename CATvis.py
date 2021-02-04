from neuprint import Client, fetch_custom
import pandas as pd
import plotly.express as px
import plotly as pio
import json
import numpy as np




def connectivity_sunburst(df:pd.DataFrame, column:str):
    """
    connectivity_sunburst takes a column from a dataframe that contains roiInfo 
    json information between two neurons(usually pulled from neuPrint)
    and generates an interactive sunburst plot that shows which rois and 
    sub rois these connections occur in. 

    Args:
        df (pd.DataFrame): dataframe containing connections between neurons
        column (str): name of the column containing connectivity information roiInfo

    Returns:
        Figure: sunburst plot indicating which ROIs and sub rois your connections occur in 
    """    


    # adds a synapse count column to roi 'hierarchy' df copy that acts as a running 
    # tally of the number of synapses in that ROI for your specified df/column
    

    # copy the dataframe, make a new column that reads the column of interest as a json dict
    dfplot = df.copy()
    dfplot['json']=dfplot[column].apply(json.loads)
    
    # read hierarchy or ROIs spreadsheet
    hierarchy = pd.read_csv('ROI_hierarchy.csv')

    # add a new column "synapse count" where each cell in that column = 0
    hierarchy['synapse_count'] = [0]*len(hierarchy)


    
    # count how many synapses are in each ROI 
    for roi_dict in dfplot['json']:
        
        for roi, syn in roi_dict.items():
            # go through the dict and add synapses from each ROI to 
            # the respective ROI synapse count in the hierarchy df.


            # sometimes pre=1 and post = null (or vice versa) if the 
            # synapse is on the edge of an ROI. Account for that here:
            try: 
                syn = syn['pre']
            except:
                syn = syn['post']
                

            # add that syn number to that roi's synapse count in 
            # the hierarchy graph

            hierarchy.loc[hierarchy[hierarchy['ROI_all'] == roi].index,'synapse_count'] += syn
     
    # remove rois with a synapse count of 0
    hierarchy = hierarchy[hierarchy['synapse_count'] != 0]
    
    # remove rows where the global ROI is the same as the roi_all,
    # unless there is only one row with that global ROI.
    global_counts = (hierarchy['Global'].value_counts())
    for idx, row in hierarchy.iterrows():
        
        if global_counts[row['Global']] == 1:
            continue
        elif row['ROI_all'] == row['Global']:
            hierarchy.drop(idx, inplace=True)
        else:
            continue 
                
    # this is only ploting Global ROIs and their direct sub ROIs. 
    sbplot = px.sunburst(hierarchy, path=['Global','ROI'], values='synapse_count')
   

    return sbplot


