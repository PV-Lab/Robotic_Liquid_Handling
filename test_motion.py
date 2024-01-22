from opentrons import protocol_api

#metadata about protocol. 
#NOTE "apiLevel" can appear here or in requirements, but not in both places.
metadata = {
    "protocolName": "Test Positioning",
    "author": "Evan Hutchinson <ehutch03@mit.edu>",
    "description": "test OT2's ability to move the pipette around with and without a tip. No liquid yet",
}

requirements = {"robotType": "OT-2", "apiLevel": "2.16"} 


def run(protocol: protocol_api.ProtocolContext):
    #labware TODO need to switch labware to what's actually going to be used
    plate = protocol.load_labware("nest_96_wellplate_200ul_flat",location="2")
    # TODO switch the plate name and deck location to what is physically on the robot, 
    # also make these variables once passed unit test 
    tiprack = protocol.load_labware("opentrons_96_tiprack_1000ul",location="8")

    #pipettes 
    right_pipette = protocol.load_instrument("p1000_single_gen2",mount="right",tip_racks=[tiprack])


    #---commands---# 
    
    # commment this out in order to test without a tip instead
    right_pipette.pick_up_tip(tiprack.wells()[0]) # idx 0 of the tiprack's wells is well A1
    #-----------test manual movement-----------#

    # right_pipette.move_to(plate["A1"].top()) # go to top of the well plate
    # # protocol.pause("is the robot above the top of well A1?")
    # right_pipette.move_to(plate["H12"].top()) # go to bottom of well plate
    # # protocol.pause("is the robot positioned above well H12?")
    # right_pipette.move_to(plate["A1"].top(z=10)) # go back to the top of the well plate and move 10mm above its bottom
    # # protocol.pause("has the robot moved back to well A1?")
    # right_pipette.move_to(plate["A1"].bottom(),force_direct=True) # lower the pipette down to bottom of well A1 directly


    #-------------test automated movement via looping to go to every well in 2 rows--------#
    for letter in "AB":
        for num in range(1,13):
            right_pipette.move_to(plate[f"{letter}{num}"].top())

    right_pipette.drop_tip(tiprack.wells()[0]) 