ABC1 

ABC2

molarity_grad = [1, 0.8, 0.5, 0.3]

#test 4 molarities of each salt so 4 individual liquids per salt.

# take first salt and test for second salt

#user should be able to input temperature, specify solute & solvent, how much liquid you want to add to each vial and how many (some solvents may need 2 liquids).
# also add temp & shaking routine 

# want all of this data stored in a csv file for the name of salt, vol solvent, name of solvent, vol solvent, shaking routine (duration, etc.)
# 

# NOTE step 0 is you load in the csv file in a pandas dataframe. initially act as if user only needs 1 salt. 
# dataframe would show salt, solvent/acid you're adding, the molarity of it & how much is being added

# NOTE INITIALLY TESTING ON ONE ACID AND ONE SALT, FIGURE OUT DIFFERENT COLUMN LENGTHS LATER

# --USER INPUT CSV-- #
# e.g. COLUMN0: salt barcode for safety tracking efficiency COLUMN1: salt, COLUMN2: molar mass, COLUMN3: what is the molarity you're adding (mulitply molar mass by molarity spec) COL 3.5: solvent/acid barcode COLUM4: solvent/acid name, COL5: molarity, COL6: amount

# after user inputs this, the protocol reads it and converts it into new dataframe with all user inputs and 1 new columns of actual volume in a given vial(mass of salt).

# now opentrons starts running. Need to know exactly 

# NOTE SOLUBILITY OR ANY KIND OF STOCK SOLUTION MAKING EVERYTHING NEEDS TO HAPPEN IN VIALS SO THEY CAN BE CAPPED. 
# vials will already be inside of heater & shaker, acid is elsewhere.
# fix locations of acids & salts. add protocolPause that flashes on screen to say "are you sure your acids are here, salts here?"


class Solubility_testing:
    def __init__(self) -> None:
        

