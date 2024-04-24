# data = {'date': {0: 3122024}, 'owner': {0: 'basitadas'}, 'salt': {0: 'Lead iodide'}, 'formula': {0: 'PbI2'}, 'barcode': {0: 203409}, 
#         'purity': {0: 99.9999}, 'molar mass (mg)': {0: 'molar mass'}, 'mass in vial': {0: 361.01}, 'acid': {0: 'Hydrogen bromide'}, 
#         'formula.1': {0: 'HBr2'}, 'barcode.1': {0: 504309}, 'concentration': {0: '47%'}, 'volume (ml)': {0: 1}, 'remarks': {0: None}}

# print(data['salt'][0])
# print(data['acid'][0])
# print(data['molar mass (mg)'][0])

# def assign_spots(data,ingredient) -> dict:
#     ''' 
#     given a dictionary of information about salts
#     and acids in use, assign locations to each of them
#     (as of now, salts will be inside of heater & shaker,
#     acid stored elsewhere). As of 3/13/24 going to assume the given piece of hardware
#     has a 96 well plate on top of it, but the way positions calculated
#     can be switched easily
#     '''
#     if ingredient.lower() == 'salt':
#         # num_ingredient = len(data['salt'][0]) # NOTE one ingredient for now, this is also still bugged
#         num_ingredient = 4
#         print('assigning salt spots...')
#         print('ingredient: ', data['salt'][0]) # NOTE if multiple salts convert to list instead
#         ingredient_name = data['salt'][0]

#     elif ingredient.lower() == 'acid':
#         # print(data['acid'][0])
#         # num_ingredient = len(data['acid'].values()[0])   
#         num_ingredient = 1
#         print('assigning acid spots...')
#         print('ingredient: ', data['acid'][0]) # NOTE if multiple acids convert to list instead
#         ingredient_name = data['acid'][0]
#     elif ingredient.lower() != 'acid' and ingredient.lower() != 'salt':
#         raise AssertionError('specify whether adding acids or salts!')

#     print(f'{num_ingredient=}')
#     row_map = {1: 'A', 2:'B', 3:'C', 4:'D', 5:'E', 6:'F', 7:'G', 8:'8'}
#     shaker_positions = {} # TODO, in line with keeping track of written names instead of numerical titles of each
#     # will need to switch the logic of how this dictionary is initialized

#     for i in range(1,num_ingredient+1): # TODO switch this to enumerating through dictionary so users can read off the names/formulae directly instead of 'salt 1'
#         vial_letter = row_map[int(i / 12) if int(i/12) != 0 else 1]
#         vial_number = i % 12
        
#         shaker_positions[i] = f'{vial_letter}{vial_number}' # TODO once using multiple acids, keep track of multiple names by mapping them 
#         # in a list and then iterating through them as opposed to storing a single static ingredient name

#     print('Dictionary of positions: ', shaker_positions)
#     return shaker_positions 


    
# salt_locations = assign_spots(data,'salt')
# print('result of call: ', salt_locations)
# print('first acid location: ', salt_locations[list(salt_locations.keys())[0]])

# print(salt_locations.items())
# for salt, location in salt_locations.items():
#     print('salt location(s): ', location)
#     print('salt: ', salt)
#     print(f'is there a vial located at {location}?')

# class Solution:
#     id = 0
#     def __init__(self) -> None:
#         Solution.id += 1
        

# s = Solution()
# print(f'{s.id=}')
# b = Solution()
# print(f'{b.id=}')

# print(Solution.id)

solution1 = Solution('Cs')
solution2 = Solution('Pb')
solution3 = Solution('Br')

microtiter = LABWARE['microtiter_plate']

possible_compounds = find_compounds('Cs', 'Pb', 'Br') # output is list of ratios with ONLY these 3 elements, where either inter or intrastate is true

all_ratios = []
# for compound in possible_compounds: 
#    compound_dict = mg.Composition.asdict(mg.Composition(compound))
#    one_comp_proportion = []
#    for element in compound_dict.keys(): 
#         compound_ratio = comp.get_wt_fraction(Element("element"))
#         one_comp_proportion.append(compound_ratio)
#    all_ratios.append(one_comp_proportion)
# #to actually mix one of these
# example_ratio = {'Cs': 0.25, 'Pb':0.25, 'Br':0.5}

well_volume = 2000 # using 5mL now 


####---PROTOCOL STEPS---####

            #--not uploaded to opentrons--# 
# scan through csv file for compounds containing ONLY the elements specified, where either inter or intrastate is true
# of these compounds, look in the corresponding atoms column and pull out the first two numbers to get the ratio of solution A to solution B
# save these to a list as all of the compounds you want to look at.
            #--not uploaded to opentrons--#

# copy paste the list of compounds to experiment with into the protocol/select 5 of them

            #--opentrons instructions--#
# stock solution A located at some reservoir
# stock solution B located at some other reservoir
# compounds to be mixed in 5 wells/vials of your selected labware


# opentrons picks up tip
# opentrons goes through 5 wells to dispense each of the 5 volumes of A into the destination wells
# opentrons drops tip
# opentrons goes through 5 wells to dispense each of the 5 volumes of B into the destination wells 
            #--separately from the opentrons instructions--#

# save the list of 5 compounds you experimented with to a csv or something similar in order to keep track of what has been tested





def create_comp(compounds, max_volume):
    for idx, volume in enumerate(five_volumes):
        soln_A = row_A[idx]
        soln_B = row_B[idx]
        for idx,compound in enumerate(compounds):
           A_ratio = compound[idx] 
           pipette.aspirate(A_ratio,row[idx])
           pipette.drop_tip()
           B_ratio = compound[d]


# for compound in possible_compounds:
#     (ratio1, ratio2) = compound

def make_comp(compound_ratio, destination):
    for elem in compound_ratio.keys():
        elem_mass_fraction = compound_ratio[elem] #the weight fraction of the compound 
        elem_vol_fraction = elem_mass_fraction / elem_density # NOTE maybe we don't need to convert the mass fraction?
        
        pipette.pick_up_tip()
        pipette.aspirate(elem_vol_fraction,elem_location)
        pipette.dispense(elem_vol_fraction,destination)
        pipette.drop_tip()

make_comp(example_ratio,microtiter) #this would make a 1:1:2 ratio of CsPbBr by weight in well A1 of the microtiter plate


