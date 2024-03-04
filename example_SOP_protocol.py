from opentrons import protocol_api
from opentrons import types

metadata = {
    "protocolName":"Example Protocol",
    "author":"John Doe",
    "description":"Insert a brief description of what the protocol intends to do",
}

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

def run(protocol: protocol_api.ProtocolContext):
    #----load in labware here----# 
    plate = protocol.load_labware("nest_96_wellplate_200ul_flat",location="2")
    tiprack = protocol.load_labware("opentrons_96_tiprack_1000ul",location="8")

    #----load in pipette(s) here----#
    right_pipette = protocol.load_instrument("p1000_single_gen2",mount="right",tip_racks=[tiprack])
    #----instructions for OT-2 here----#
    right_pipette.pick_up_tip(tiprack["E11"])

    right_pipette.aspirate(50, plate["A1"])
    right_pipette.dispense(50, plate["B2"])

    right_pipette.drop_tip()

    