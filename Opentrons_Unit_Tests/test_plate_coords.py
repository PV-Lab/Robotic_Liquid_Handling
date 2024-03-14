
from opentrons import protocol_api
from opentrons import types

metadata = {
    "protocolName":"Test Custom Coordinates",
    "author":"Evan Hutchinson",
    "description":"Test whether manually defined positions in python are reliable",
}

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

def run(protocol: protocol_api.ProtocolContext):
    #----load in labware here----# 
    plate = protocol.load_labware("nest_96_wellplate_200ul_flat",location="2")
    
    tiprack = protocol.load_labware("opentrons_96_tiprack_1000ul",location="8")

    #----load in pipette(s) here----#
    right_pipette = protocol.load_instrument("p1000_single_gen2",mount="right",tip_racks=[tiprack])

    
    #----load in liquids or other locations here----#
    water_tip = tiprack["E11"]
    plate_coords = {'A1': (16, 68, 40), 'A2': (39, 68, 40), 'A3': (62, 68, 40), 'A4': (85, 68, 40), 'A5': (108, 68, 40), 
                    'B1': (16, 45, 40), 'B2': (39, 45, 40), 'B3': (62, 45, 40), 'B4': (85, 45, 40), 'B5': (108, 45, 40), 
                    'C1': (16, 22, 40), 'C2': (39, 22, 40), 'C3': (62, 22, 40), 'C4': (85, 22, 40), 'C5': (108, 22, 40),}
    #----instructions for OT-2 here----#
    right_pipette.pick_up_tip(water_tip)
    for letter in "AB":
        for num in range(1,5):
            x_pos, y_pos, z_pos = plate_coords[f"{letter}{num}"]
            right_pipette.move_to(types.Location(types.Point(x=x_pos, y=y_pos, z=z_pos), None))
    right_pipette.drop_tip(water_tip)
