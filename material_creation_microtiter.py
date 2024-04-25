import pandas as pd
import numpy as np

from opentrons import protocol_api

metadata = {
    "protocolName":"Material Creation",
    "author":"Evan Hutchinson",
    "description":"Create a series of materials from 2 stock solutions",
    "apiLevel": "2.16",
}

LABWARE = {
        '1mL_pipette':'p1000_single_gen2',
        'microtiter_plate':'nest_96_wellplate_200ul_flat', # NOTE check that max volume is indeed 200uL
        '6_tube_tuberack':'opentrons_6_tuberack_falcon_50ml_conical',
        'opentrons_tiprack':'opentrons_96_tiprack_1000ul',
    }

manual_material_dict = {'composition': {0: 'Cs1Pb1Br3', 1: 'Cs1Pb2Br5', 2: 'Cs2Pb1Br4', 3: 'Cs2Pb3Br8', 4: 'Cs2Pb5Br12'}, 'Atoms': {0: '[1, 1, 3]', 1: '[1, 2, 5]', 2: '[2, 1, 4]', 3: '[2, 3, 8]', 4: '[2, 5, 12]'}, 'ratio_1': {0: 1, 1: 1, 2: 2, 3: 2, 4: 2}, 'ratio_2': {0: 1, 1: 2, 2: 1, 3: 3, 4: 5}}
# {'composition': 
#                         {0: 'Rb1Bi1Br4', 1: 'Rb1Bi2Br7', 2: 'Rb2Bi1Br5', 3: 'Rb2Bi3Br11', 4: 'Rb3Bi1Br6', 5: 'Rb3Bi2Br9', 6: 'Rb4Bi3Br13', 7: 'Rb5Bi2Br11'}, 
#                         'Atoms': 
#                         {0: '[1, 1, 4]', 1: '[1, 2, 7]', 2: '[2, 1, 5]', 3: '[2, 3, 11]', 4: '[3, 1, 6]', 5: '[3, 2, 9]', 6: '[4, 3, 13]', 7: '[5, 2, 11]'}, 
#                         'ratio_1': {0: 1, 1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 4, 7: 5}, 
#                         'ratio_2': {0: 1, 1: 2, 2: 1, 3: 3, 4: 1, 5: 2, 6: 3, 7: 2}
#                         }

mat_to_make = pd.DataFrame(manual_material_dict)

# mat_to_make = pd.read_csv('output/materials_to_make.csv')
mat_dict = mat_to_make.to_dict()
print(mat_dict)
num_mats = len(mat_to_make)
print(40 * '-')
print('Materials to make: \n',mat_to_make)
print(40*'-')
print(f'{num_mats=}')


A_column = mat_to_make['ratio_1']
B_column = mat_to_make['ratio_2']

parts_per_material = []
A_parts = []
B_parts = []

for part_a, part_b in zip(A_column, B_column):
    
    A_parts.append(part_a)
    B_parts.append(part_b)
    parts_per_material.append(part_a+part_b)


print(40*'-')
print(f'{parts_per_material=}')
print(f'{A_parts=}')
print(f'{B_parts=}')




def run(protocol:protocol_api.ProtocolContext) -> None:
    tiprack = protocol.load_labware(LABWARE['opentrons_tiprack'],6)
    pipette = protocol.load_instrument(LABWARE['1mL_pipette'],mount='right',tip_racks=[tiprack])
    tuberack = protocol.load_labware(LABWARE['6_tube_tuberack'],9)  
    
    

    heater_shaker = protocol.load_module('heaterShakerModuleV1', location='4') # NOTE placed in spot 9 so less splash hazard
    
    heater_shaker_plate = heater_shaker.load_labware(LABWARE['microtiter_plate'])
    heater_shaker.close_labware_latch()
    heater_shaker.set_target_temperature(37)
    soln_A = tuberack['A1']
    soln_B = tuberack['A2']

    def make_series(material_instructions, max_volume) -> None: # NOTE once you switch to the OOP approach remove volume argument & read it off from the vial/solution
        '''
        expects: 
            material_instructions: a dictionary of material instructions from get_recipes
            max_volume: the volume of liquid allowed per well/vial (in uL)

        assigns spots to labware, pulls liquid from solution A and B to mix them as necessary
        '''
        
        pipette.pick_up_tip(tiprack['A1'])
        
        for idx, num_parts in enumerate(parts_per_material):
            one_part_volume = max_volume / num_parts # NOTE these variable names def need work
            
            a_volume = one_part_volume * A_parts[idx]
            pipette.transfer(a_volume, tuberack['A1'].bottom(z=30), heater_shaker_plate[f'A{idx+2}'].center(),new_tip='never')
            
            
        
        pipette.drop_tip()
        
        pipette.pick_up_tip(tiprack['B1'])

        for idx, num_parts in enumerate(parts_per_material):
            one_part_volume = max_volume / num_parts # NOTE these variable names def need work
            
            b_volume = one_part_volume * B_parts[idx]
            pipette.transfer(b_volume, tuberack['A2'].bottom(z=30), heater_shaker_plate[f'A{idx+2}'].center(),new_tip='never')
        
        pipette.drop_tip()    

        
        
    make_series({}, 150)
    heater_shaker.set_and_wait_for_shake_speed(500)
        
    protocol.delay(minutes=1)
    heater_shaker.deactivate_heater()
    heater_shaker.deactivate_shaker()
# mat_to_make['composition'].to_csv('output\materials_made.csv',index=False)
# print('Materials experimented with saved to csv file!')
