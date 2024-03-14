from opentrons import protocol_api
from opentrons import types

metadata = {
    "protocolName":"Test Volume",
    "author":"Evan Hutchinson",
    "description":"Test whether how accurately the OT-2 can repeatedly dispense the same volume of water",
}

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

def run(protocol: protocol_api.ProtocolContext):
    #----load in labware here----# 
    tiprack = protocol.load_labware("opentrons_96_tiprack_1000ul",location="8")

    water_location = types.Location(types.Point(x=16,y=68,z=20),None) # NOTE the Z offset is CRITICAL so you don't have a collision. FIX WHERE THESE LOCATIONS ACTUALLY ARE
    
    row_2 = [types.Location(types.Point(x=(16 + num * 23), y=45, z=40), None) for num in range(3,5)]

    #----load in pipette(s) here----#
    right_pipette = protocol.load_instrument("p1000_single_gen2",mount="right",tip_racks=[tiprack])
    #----instructions for OT-2 here----#
    right_pipette.pick_up_tip(tiprack["E11"])
    
    for well in row_2:
        right_pipette.aspirate(600, water_location)
        right_pipette.dispense(600, well)
        
    
    right_pipette.drop_tip(tiprack["E11"])
