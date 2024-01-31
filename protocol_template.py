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


    #----load in pipette(s) here----#
    
    
    #----load in liquids or other locations here----#


    #----instructions for OT-2 here----#
