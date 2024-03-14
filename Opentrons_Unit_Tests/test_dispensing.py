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
    
    water_location = types.Location(types.Point(x=16,y=68,z=40),None) # NOTE the Z offset is CRITICAL so you don't have a collision. FIX WHERE THESE LOCATIONS ACTUALLY ARE

    #---pipette dry and wet runs below. comment out move to lines & switch them with aspirate/dispense for toggling between wet and dry modes---#
    right_pipette = protocol.load_instrument("p1000_single_gen2",mount="right",tip_racks=[tiprack])
    
    right_pipette.pick_up_tip(tiprack["E11"])
    
    #----aspirate 50ul into A1 and B1-B10, then 100ul into B11----#
    # right_pipette.move_to(water_location)
    # right_pipette.aspirate(50, water_location)
    # # protocol.pause("check tip location")

    # # right_pipette.move_to(plate["A1"].top())
    # right_pipette.dispense(50, plate["A1"])
    # # protocol.pause("did you make it to a1?")

    # right_pipette.aspirate(600, water_location)
    # for num in range(1,11): 
    #     # right_pipette.move_to(plate[f"B{num}"].top())
    #     right_pipette.dispense(50, plate[f"B{num}"])
    # # protocol.pause("did you make it to each of the first 10 cells in B?")
    # right_pipette.dispense(100, plate["B11"])
    #----aspirate 50ul into A1 and B1-B10, then 100ul into B11----#


    #-----test if the volumes aspirated/dispensed are accurate----#
    for num in range(1,11):
        right_pipette.aspirate(100, water_location)
        right_pipette.dispense(100, plate[f"C{num}"])
    #-----test if the volumes aspirated/dispensed are accurate----#
        

    right_pipette.drop_tip(location=tiprack["E11"])
    # NOTE  change from the tiprack to the trash chute once you start using things besides pure water

    

    
    
