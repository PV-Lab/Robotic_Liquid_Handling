from opentrons import protocol_api
from opentrons import types

metadata = {
    "protocolName":"Test Dyes Mixed",
    "author":"Evan Hutchinson",
    "description":"Test if the OT-2 can aspirate liquids properly by creating a gradient of blue and green dyed water",
}

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

def run(protocol: protocol_api.ProtocolContext):
    #----load in labware here----# 
    plate = protocol.load_labware("nest_96_wellplate_200ul_flat",location="2")
    
    tiprack = protocol.load_labware("opentrons_96_tiprack_1000ul",location="8")

    #----load in pipette(s) here----#
    right_pipette = protocol.load_instrument("p1000_single_gen2",mount="right",tip_racks=[tiprack])
    water_tip = tiprack["E11"]
    green_tip = tiprack["B11"]
    blue_tip = tiprack["A11"]
    
    #----load in liquids or other locations here----#
    green_dye = plate["A1"]
    blue_dye = plate["A2"]
    water_location = types.Location(types.Point(x=16,y=68,z=20),None)
    #----instructions for OT-2 here----#
    right_pipette.pick_up_tip(water_tip)

    for num in range(1,11):
        right_pipette.aspirate(150, water_location)
        right_pipette.dispense(150, plate[f"C{num}"].top())
        # right_pipette.move_to(water_location)
        # right_pipette.move_to(plate[f"B{num}"].top())


    right_pipette.aspirate(300, water_location)
    right_pipette.dispense(150, green_dye.top())
    right_pipette.dispense(150, blue_dye.top())
    # right_pipette.move_to(water_location)
    # right_pipette.move_to(green_dye.top())
    # right_pipette.move_to(blue_dye.top())

    right_pipette.drop_tip(water_tip)

    right_pipette.pick_up_tip(green_tip)
    for num in range(1,11):
        right_pipette.aspirate(1 * num, green_dye.bottom())
        right_pipette.dispense(1 * num,plate[f"C{num}"].bottom())
        # right_pipette.move_to(green_dye.bottom())
        # right_pipette.move_to(plate[f"B{num}"].top())


    right_pipette.drop_tip()

    right_pipette.pick_up_tip(blue_tip)
    for num in range(10, 0, -1):
        right_pipette.aspirate(1 * num, blue_dye.bottom())
        right_pipette.dispense(1 * num, plate[f"C{11-num}"].bottom())
        # right_pipette.move_to(blue_dye.bottom())
        # right_pipette.move_to(plate[f"B{num}"].top())
    for num in range(1,11):
        right_pipette.mix(2, 160, plate[f"C{num}"])
    
    right_pipette.drop_tip()
    





    