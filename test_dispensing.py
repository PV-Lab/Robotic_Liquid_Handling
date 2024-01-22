from opentrons import protocol_api
from opentrons import types


metadata = {
    "protocolName":"Test Dispensing",
    "author": "Evan Hutchinson",
    "description": "Test OT-2's ability to aspirate and dispense liquids both once and repeatedly. Using H2O for now.",
}

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

def run(protocol: protocol_api.ProtocolContext):
    # labware
    plate = protocol.load_labware("nest_96_wellplate_200ul_flat",location="2")
    
    tiprack = protocol.load_labware("opentrons_96_tiprack_1000ul",location="8")

    # position of the water source in mm (x,y,z)
    # TODO find position of the water tube and put it here
    
    water_location = types.Location(types.Point(x=0,y=0,z=0),None) # NOTE the Z offset is CRITICAL so you don't have a collision. FIX WHERE THESE LOCATIONS ACTUALLY ARE


    #pipette
    right_pipette = protocol.load_instrument("p1000_single_gen2",mount="right",tip_racks=[tiprack])
    #right_pipette.pick_up_tip(tiprack["G11"])
    right_pipette.move_to(water_location)
    # right_pipette.drop_tip(location=tiprack["G11"])
    # NOTE TEST THE ABOVE BEFORE YOU UNCOMMENT THE BELOW WHERE YOU PICK UP THE WATER. DIAL IN X, Y, AND Z

    # #---test picking up and dispensing water once---#  NOTE you need to decide what to do with the wet tips. Thinking you reuse them once per day.
    # right_pipette.pick_up_tip(tiprack["G11"]) # inside of pick_up_tip can specify tip A1 by saying pick_up_tip(tiprack.wells()[0]) 
    # right_pipette.aspirate(100, water_location) 
    # right_pipette.dispense(100, plate["A1"])

    # #---test picking up and dispensing water 10 times---# 
    # right_pipette.aspirate(600, water_location)
    # for num in range(1,11):
    #     right_pipette.dispense(50, plate[f"B{num}"]) #dispense 50ul into 10 plates in row B
    # right_pipette.dispense(100, plate["B11"]) # empty pipette by dispensing 100ul into cell B11

    # right_pipette.drop_tip() # drop the tip into the trash chute once done. NOTE remember to empty this out when you're finished with it

    
    
