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
    pipette = protocol.load_instrument("p1000_single_gen2",mount="right",tip_racks=[tiprack])
    
    
    #Powders:

    #Cesium acetate
    Cs_Ac = Powder(molar_mass = 191.95)

    #Antimony(III) bromide
    Sb_Br3 = Powder(molar_mass = 361.47)

    #Rubidium bromide
    Rb_Br = Powder(molar_mass = 165.3718)

    #Indium(III) bromide
    In_Br3 = Powder(molar_mass = 354.53)

    powders = [Cs_Ac, Sb_Br3, Rb_Br, In_Br3]

    # NOTE for sake of reusability I'm thinking we automatically assign deck locations for powders
    powder_locations = assign_dry_spots(powders)

    #---stock_vials = [Cs_Ac_stock_vial, Sb_Br3_stock_vial, RbBr_stock_vial, In_Br3_stock_vial]---# <-- <-- otto's implementatino

    # NOTE similarly, we can automatically assign where the stock vials go since it shouldn't be of importance
    stock_vials = make_stock_vials(powder_locations)

    #Liquids:
    #Hydrobromic Acid (9M)
    H_Br = Solution(molarity = 9)

    #Hydrochloric Acid (9M)
    H_Cl = Solution(molarity = 9)

    #Hydroiodic Acid (9M)
    H_I = Solution(molarity = 9)

    #MIXING STOCK SOLUTIONS (volume in Liters)
    # CsAc - 1M
    # RbBr - 0.5M
    # SbBr3 - 1M
    # InBr3 = 1M

    stock_volume = 0.500

    Cs_Ac_HBr = Solution(molarity = 1)
    Rb_Br_HBr = Solution(molarity = 0.5)
    Cs_Ac_HBr = Solution(molarity = 1)
    Cs_Ac_HBr = Solution(molarity = 1)

    # NOTE question: difference between stock vial and stock solution?
    stock_solutions = [Cs_Ac_HBr,Rb_Br_HBr,Cs_Ac_HBr,Cs_Ac_HBr]


    for i in len(powders):
        # NOTE powder deposition would likely have to be done by hand until we get the flex's robot arm
       # powder_depositer.deposit(location = stock_vials[i], mass = powders[i].molar_mass*stock_volume*stock_solutions[i].molarity)
    for i in len(powders):
	    pipette.aspirate(location = HbBr_vial, volume = stock_volume)
	    pipette.dispense(location = stock_vials[i])
         
    #MAKING A NANOCRYSTAL SOLUTION

    #Define Target Compound Ratio
    #Starting with formula AxByCz
    #Assume that z is already determined by x and y, (i.e we only need to care about x and y)
    #Example: Rb3Sb2Br9
    A_stock = Rb_Br_Hbr
    B_stock = Sb_Br3_HBr
    vial_volume = 0.010

    x=3
    y=2
    # z=9 (already determined by x and y) NOTE what does this calculation look like for getting 9 from this?
    # NOTE if it's just charge neutrality then this should be straightforward. 

    volA = vial_volume*x/(x+y)
    volB = vial_volume*y/(x+y)

    pipette.aspirate(location = A_stock.vial, volume = volA)

    pipette.dispense(vial1)

    pipette.aspirate(location = B_stock.vial, volume = volB)

    pipette.dispense(vial1)

    #COMPOSITION GRADIENT

    x1 = 3 
    y1 = 2

    x2 = 3
    y1 = 1

    volA1 = volume*x1/(x1+y1)
    volB1 = volume*y1/(x1+y1)

    volA2 = volume*x1/(x1+y1)
    volB2 = volume*y1/(x1+y1)

    #Number of vials:
    N = 40
    for i in range(N+1):
        pipette.aspirate(location = A_stock.vial, volume = (volA1*i + volA2*(N-i))/N)
        pipette.dispense(vials[i])
        pipette.aspirate(location = B_stock.vial, volume = (volB1*i + volB2*(N-i))/N)
        pipette.dispense(vials[i])

        
