from opentrons import protocol_api
from opentrons import types

metadata = {
    "protocolName":"Test 96 Well Gradient",
    "author":"Evan Hutchinson",
    "description":"Emulate the process of creating a gradient of precursor mixtures, starting from dry measured salts and ending with a gradient of two mixtures",
}

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}

def run(protocol: protocol_api.ProtocolContext):
    #----load in labware here----# 
    plate = protocol.load_labware("nest_96_wellplate_200ul_flat",location="2")
    
    tiprack = protocol.load_labware("opentrons_96_tiprack_1000ul",location="8")


    #----load in pipette(s) here----#
    right_pipette = protocol.load_instrument("p1000_single_gen2",mount="right",tip_racks=[tiprack])
    left_pipette = None
    water_tip = tiprack["E11"]
    green_tip = tiprack["B11"]
    blue_tip = tiprack["A11"]    
    
    #----load in liquids or other locations here----#
    water_location = types.Location(types.Point(x=16,y=68,z=20),None)
    stock_soln_1 = types.Location(types.Point(x=16+23, y=68, z=2), None)
    stock_soln_2 = types.Location(types.Point(x=16+46, y=68, z=2), None)


    #----instructions for OT-2 here----#
    # def get_water(letter, num):
    #     right_pipette.aspirate(200, water_location)
    #     right_pipette.dispense(200, plate[f"{letter}{num}"])
    def add_solvent():
        """
        Add the solvent (for this test water) to the salts (food dye) that are in a specified location on the deck
        """
        for _ in range(4):
            right_pipette.aspirate(1000, water_location)
            right_pipette.dispense(1000, types.Location(types.Point(x=16+23, y=68, z=25), None)) # need to aspirate above dye level 
            right_pipette.aspirate(1000, water_location)
            right_pipette.dispense(1000, types.Location(types.Point(x=16+46, y=68, z=25), None))
        
        # NOTE: NEED TO DROP & SWAP TIPS HERE AS WELL?
        
        #---- DRY VERSION ----#
        # right_pipette.move_to(water_location)
        # right_pipette.move_to(stock_soln_1)
        # right_pipette.move_to(water_location)
        # right_pipette.move_to(stock_soln_2)

        swap_tips("right")

    def get_dyes(well, amount, solution):     
        letter, num = well
        
        current_well = plate[f"{letter}{num}"]
        right_pipette.aspirate(0, current_well.top()) #NOTE instead of aspirating 0ul above the current well, do it above the previous well

        right_pipette.aspirate(amount,solution)
        right_pipette.dispense(amount, current_well.bottom())
        right_pipette.blow_out(current_well) # dispense another time while above the well to clear the nozzle

        #---- DRY VERSION ---- #
        # right_pipette.move_to(current_well.top())

        # right_pipette.move_to(solution)
        # right_pipette.move_to(current_well.bottom())
        

    def swap_tips(pipette):
        """
        Assumes a tip is loaded onto the OT-2 at the start of the protocol, then subsequently drops and picks one up as needed
        """
        if pipette == "right":
            right_pipette.drop_tip()
            right_pipette.pick_up_tip()
        elif pipette == "left":
            left_pipette.drop_tip()
            left_pipette.pick_up_tip()
        elif pipette == "96":
            # NOTE want to add functionality for using all 96 tips at once and instead switching the tiprack
            pass
        else:
            raise AssertionError("Need to provide the side as 'left', 'right', or indicate you are using the '96' tip head instead!")
    
    def make_gradient(): # really would name this make precursor or something?
        for step in range(2):
            increment = 0
            for idx, letter in enumerate("ABCDEFGH"):
                for num in range(1,13):
                    well = (letter, num)
                    gain = 1 # scale the volume up from 100ul to 200, 300, etc. ul with gains of 2, 3, ...
                    scaling = 1.05 # scale by 1.05 to make volume min 0 and max 199.5 for easy visual inspection
                    
                    forward_amount = (95 - increment) * gain # 96 leaves 2ul in the tip due to the gain of 2, get around by doing 95 for now
                    reverse_amount = increment * gain

                    
                    if step == 0: # add some functionality for automatically going in reverse or forward order?
                        get_dyes(well, scaling * forward_amount, stock_soln_1)
                    if step == 1:
                        get_dyes(well, scaling * reverse_amount, stock_soln_2) # as of now manually specifying forward amt for step 1 and reverse amt for step 2, clean this up
                    increment += 1

            swap_tips("right")
        
    right_pipette.pick_up_tip(tiprack["F11"]) # need to start with F11 so swap tips can grab them from A0 and onward without issue
    # NOTE SWITCH FROM F11 TO SOMETHING ELSE
    # add_solvent()
    make_gradient()
    right_pipette.drop_tip() # at the very end drop any remaining tips
    
    
