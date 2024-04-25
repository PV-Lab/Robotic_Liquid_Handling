import pandas as pd
import numpy as np

from opentrons import protocol_api

metadata = {
    "protocolName":"Material Creation (Microtiter)",
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

manual_material_dict = {'composition': {0: 'Cs1Pb1Br3', 1: 'Cs1Pb2Br5', 2: 'Cs2Pb1Br4', 3: 'Cs2Pb3Br8', 4: 'Cs2Pb5Br12', 5: 'Cs3Pb1Br5', 6: 'Cs3Pb2Br7', 7: 'Cs3Pb4Br11', 8: 'Cs4Pb1Br6', 9: 'Cs4Pb2Br5', 10: 'Cs4Pb3Br7', 11: 'Cs4Pb3Br10', 12: 'Cs4Pb4Br9', 13: 'Cs4Pb5Br11', 14: 'Cs5Pb2Br9', 15: 'Cs5Pb3Br8', 16: 'Cs5Pb3Br11', 17: 'Cs5Pb4Br10', 18: 'Cs6Pb3Br9', 19: 'Cs7Pb2Br11', 20: 'Cs7Pb3Br10', 21: 'Cs7Pb4Br9'}, 'Atoms': {0: '[1, 1, 3]', 1: '[1, 2, 5]', 2: '[2, 1, 4]', 3: '[2, 3, 8]', 4: '[2, 5, 12]', 5: '[3, 1, 5]', 6: '[3, 2, 7]', 7: '[3, 4, 11]', 8: '[4, 1, 6]', 9: '[4, 2, 5]', 10: '[4, 3, 7]', 11: '[4, 3, 10]', 12: '[4, 4, 9]', 13: '[4, 5, 11]', 14: '[5, 2, 9]', 15: '[5, 3, 8]', 16: '[5, 3, 11]', 17: '[5, 4, 10]', 18: '[6, 3, 9]', 19: '[7, 2, 11]', 20: '[7, 3, 10]', 21: '[7, 4, 9]'}, 'ratio_1': {0: 1, 1: 1, 2: 2, 3: 2, 4: 2, 5: 3, 6: 3, 7: 3, 8: 4, 9: 4, 10: 4, 11: 4, 12: 4, 13: 4, 14: 5, 15: 5, 16: 5, 17: 5, 18: 6, 19: 7, 20: 7, 21: 7}, 'ratio_2': {0: 1, 1: 2, 2: 1, 3: 3, 4: 5, 5: 1, 6: 2, 7: 4, 8: 1, 9: 2, 10: 3, 11: 3, 12: 4, 13: 5, 14: 2, 15: 3, 16: 3, 17: 4, 18: 3, 19: 2, 20: 3, 21: 4}}
# {'composition': 
#                         {0: 'Rb1Bi1Br4', 1: 'Rb1Bi2Br7', 2: 'Rb2Bi1Br5', 3: 'Rb2Bi3Br11', 4: 'Rb3Bi1Br6', 5: 'Rb3Bi2Br9', 6: 'Rb4Bi3Br13', 7: 'Rb5Bi2Br11'}, 
#                         'Atoms': 
#                         {0: '[1, 1, 4]', 1: '[1, 2, 7]', 2: '[2, 1, 5]', 3: '[2, 3, 11]', 4: '[3, 1, 6]', 5: '[3, 2, 9]', 6: '[4, 3, 13]', 7: '[5, 2, 11]'}, 
#                         'ratio_1': {0: 1, 1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 4, 7: 5}, 
#                         'ratio_2': {0: 1, 1: 2, 2: 1, 3: 3, 4: 1, 5: 2, 6: 3, 7: 2}
#                         }

mat_to_make = pd.DataFrame(manual_material_dict)
# 
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


def give_me_spots(num_ingredient):
    row_map = {1: 'A', 2:'B', 3:'C', 4:'D', 5:'E', 6:'F', 7:'G', 8:'8'}
    shaker_positions = {} # TODO, in line with keeping track of written names instead of numerical titles of each
    # will need to switch the logic of how this dictionary is initialized

    for i in range(1,num_ingredient+1): # TODO switch this logic around once it comes time to calculate with multiple salts. 
        vial_letter = row_map[int(i / 12)+1]
        vial_number = i % 12
        if vial_number == 0:
            vial_number = 1
        
        shaker_positions[i] = f'{vial_letter}{vial_number}' # NOTE if you switch from keeping track of acids numerically to keeping track of them by name, the logic for how you
        # calculate the corresponding acid volume needs to change

    #print('Dictionary of positions: ', shaker_positions)
    return list(shaker_positions.values())

print('testing spot assignment')
spots = give_me_spots(44)
print(give_me_spots(44))
every_other_spot = spots[::2]
print(f'{every_other_spot=}')

def run(protocol:protocol_api.ProtocolContext) -> None:
    tiprack = protocol.load_labware(LABWARE['opentrons_tiprack'],6)
    pipette = protocol.load_instrument(LABWARE['1mL_pipette'],mount='right',tip_racks=[tiprack])
    tuberack = protocol.load_labware(LABWARE['6_tube_tuberack'],9)  
    
    
    spots = give_me_spots(44)
    heater_shaker = protocol.load_module('heaterShakerModuleV1', location='4') # NOTE placed in spot 9 so less splash hazard
    
    heater_shaker_plate = heater_shaker.load_labware(LABWARE['microtiter_plate'])
    heater_shaker.close_labware_latch()
    # heater_shaker.set_target_temperature(37)
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
            pipette.transfer(a_volume, tuberack['A1'].bottom(z=20), heater_shaker_plate[every_other_spot[idx]].top(),new_tip='never')
            pipette.blow_out(heater_shaker_plate[every_other_spot[idx]])
            print(50*'-')
            print(mat_to_make['composition'][idx], 'in well ', every_other_spot[idx])
            print(50*'-')
        pipette.drop_tip()
        
        pipette.pick_up_tip(tiprack['B1'])

        for idx, num_parts in enumerate(parts_per_material):
            one_part_volume = max_volume / num_parts # NOTE these variable names def need work
            
            b_volume = one_part_volume * B_parts[idx]
            pipette.transfer(b_volume, tuberack['A2'].bottom(z=20), heater_shaker_plate[every_other_spot[idx]].top(),new_tip='never')
            pipette.blow_out(heater_shaker_plate[every_other_spot[idx]])
        
        pipette.drop_tip()    

        
        
    make_series({}, 200)
    # heater_shaker.set_and_wait_for_shake_speed(500)
        
    # protocol.delay(minutes=1)
    # heater_shaker.deactivate_heater()
    # heater_shaker.deactivate_shaker()
# mat_to_make['composition'].to_csv('output\materials_made.csv',index=False)
# print('Materials experimented with saved to csv file!')
