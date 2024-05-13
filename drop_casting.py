import pandas as pd
import numpy as np

from opentrons import protocol_api
from opentrons import types

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
    '''
    generate alphanumeric locations in the well plate
    based on how many different materials need to be tested
    '''
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

# print('testing spot assignment')
# spots = give_me_spots(44)
# print(give_me_spots(44))
# every_other_spot = spots[::2]
# print(f'{every_other_spot=}')

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

    def glass_slide_coordinates(length, width, border, spacing):
        '''
        return a set of x,y coordinates corresponding to locations on a 
        glass slide for drop casting

        expects:
            -length (inch) of plate along horizontal axis
            -width (inch) of plate along vertical axis
            -border (cm) of how much space to be left on all sides
            spacing (cm) of space between droplets
        '''
        length_mm = length * 2.54 * 10
        width_mm = width * 2.54 * 10
        border_mm = border * 10
        spacing_mm = spacing * 10

        xy_coords = []
        x0, y0 = (border_mm, border_mm)

        #NOTE implementation 1 using a for loop and casting everything to ints
        # for x in range(0, int(length_mm - 2 * spacing_mm), int(spacing_mm)):
        #     for y in range(0, int(width_mm - 2 * spacing_mm), int(spacing_mm)):
        #         xy_coords.append((x0 + x, y0 + y))
        
        # print('coords via for loops: ', xy_coords)
        # return xy_coords

    #NOTE implementation 2 using a while loop 
        x = border_mm
        y = border_mm

        xcoords = []
        ycoords = []
        print('length: ', length_mm)
        print('width: ', width_mm)
        while x <= (length_mm - 2*spacing_mm):
            xcoords.append(x)
            print('x: ', x)
            x += spacing_mm
            
        
        while y <= (width_mm - 2*spacing_mm):
            ycoords.append(y)
            print('y: ', y)
            y += spacing_mm

        for x in xcoords:
            for y in ycoords:
                xy_coords.append((x,y))
        print('coords via while loops: ', xy_coords)

        
        # x_points, y_points = zip(*xy_coords)
        # plt.scatter(x_points,y_points)
        # plt.show()

        points = sorted(xy_coords, key=lambda tup: tup[0])
        print(xy_coords)
        return points

    def drop_on_glass(points, volume):
        '''
        expects:
            points: a list of x,y tuples 
            volume (uL) of liquid to drop
        '''
        for coord in points:
            x_coord, y_coord = coord
            drop_location = types.Location(types.Point(x=x_coord,y=y_coord,z=0),glass_slide)
            pipette.move_to(drop_location)

            pipette.transfer(volume, heater_shaker_plate['A1'].center(),drop_location) #TODO uncomment this ONLY when you're sure it works.
    
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
        protocol.pause('look good?')   
            
            
    
        
        pipette.drop_tip(tiprack['A1'])    

        
        
    slide_points = glass_slide_coordinates(3,2,1,1.5)
    drop_on_glass(slide_points, 10)
    # drop_cast(10)
