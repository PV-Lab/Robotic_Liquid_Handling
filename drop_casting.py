import pandas as pd
import numpy as np

from opentrons import protocol_api

metadata = {
    "protocolName":"Drop Casting",
    "author":"Evan Hutchinson",
    "description":"insert description here",
    "apiLevel": "2.16",
}

LABWARE = {
        '1mL_pipette':'p1000_single_gen2',
        'microtiter_plate':'nest_96_wellplate_200ul_flat', # NOTE check that max volume is indeed 200uL
        '6_tube_tuberack':'opentrons_6_tuberack_falcon_50ml_conical',
        'opentrons_tiprack':'opentrons_96_tiprack_1000ul',
    }



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
    glass_slide = protocol.load_labware(LABWARE['microtiter_plate'],2)
    
    spots = give_me_spots(44)
    heater_shaker = protocol.load_module('heaterShakerModuleV1', location='4') # NOTE placed in spot 9 so less splash hazard
    
    heater_shaker_plate = heater_shaker.load_labware(LABWARE['microtiter_plate'])
    heater_shaker.close_labware_latch()
    # heater_shaker.set_target_temperature(37)
    soln_A = tuberack['A1']
    soln_B = tuberack['A2']
    
    def drop_cast(volume) -> None: # NOTE once you switch to the OOP approach remove volume argument & read it off from the vial/solution
        '''
        expects: 
            material_instructions: a dictionary of material instructions from get_recipes
            max_volume: the volume of liquid allowed per well/vial (in uL)

        assigns spots to labware, pulls liquid from solution A and B to mix them as necessary
        '''
        
        pipette.pick_up_tip(tiprack['A1'])
        
        # pipette.transfer(volume, heater_shaker_plate['A1'].center(),glass_slide['A1'].top(z=))
        pipette.move_to(glass_slide['A1'].top(z=30))
            
            
            
    
        
        pipette.drop_tip(tiprack['A1'])    

        
        
    drop_cast(10)
    
