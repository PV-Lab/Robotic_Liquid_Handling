import pandas as pd
import pymatgen.core as mg
import numpy as np

def identify_materials(input_data : pd.DataFrame, no_of_elems, elements : pd.Series) -> pd.DataFrame:
     elements = mg.Composition(elements).get_el_amt_dict()
     elements_keys = list(elements.keys())
     selected = input_data[(input_data['Intrastate'] == 'TRUE') | (input_data['Interstate'] == 'True')].reset_index(drop=True)
     selected['make'] = np.nan
     rows = selected.shape[0]
     for i in range(rows):
          f = selected['composition'].iloc[i]
          elems = mg.Composition(f).get_el_amt_dict()
          elems_keys = list(elems.keys())
          if elems_keys== elements_keys:
               selected['make'].iloc[i]= 'TRUE'
          else:
               selected['make'].iloc[i]= 'FALSE'
         
     print(selected)
     return selected    
     
def get_ratios(selected): 
     make = pd.DataFrame(['composition', 'ratio'])
     make= selected[['composition', 'Atoms']].copy()
     make['ratio_1'] = make['Atoms'].str.split(',').str[0]
     make['ratio_1'] = make['ratio_1'].str.split('[').str[1]
     make['ratio_2'] = make['Atoms'].str.split(',').str[1]
     make['ratio_2'] = make['ratio_2'].str.split(']').str[0]
     return make
     
      
def main(input_data : pd.DataFrame, no_of_elems, elements):
     selected = identify_materials(input_data, no_of_elems, elements)
     make = get_ratios(selected)
