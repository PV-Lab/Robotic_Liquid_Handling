import utils
import os
import pandas as Pandas


from pathlib import Path
from opentrons import protocol_api
from opentrons import types

#ABC1 

#ABC2

metadata = {
    "protocolName":"Solubility Testing",
    "author":"Evan Hutchinson",
    "description":"Evaluate the solubility of different mixtures by making a molarity gradient & seeing what dissolves",
}

requirements = {"robotType": "OT-2", "apiLevel": "2.16"}


molarity_grad = [1, 0.8, 0.5, 0.3] # NOTE for now these will be manually measured & input into the vials?

#class Solubility_testing:
#    def __init__(self) -> None:


def main(cur_dir, input_dir, output_dir):
    # read input file
    inputfile = Path(cur_dir/input_dir)
    outputfile = Path(cur_dir/output_dir)
   
    input_data = utils.read_input(inputfile)
    
    output_data = utils.create_output(input_data)

    #---test how to load it into the database---#
    dataframe_dict = Pandas.DataFrame.to_dict(output_data)
    print(f'{dataframe_dict=}')
    #------------------------------------------#

    #---test assigning spots for salts & acids---#
    assign_spots(dataframe_dict,'acid')
    #--------------------------------------------#

    #---test adding acid into the salt vials---#
    # add_acid(dataframe_dict,protocol)   # NOTE add relevant arguments to fix bugs
    #--------------------------------------------#

    #---test calculating acid volume calculation---#
    get_acid_volumes(dataframe_dict)

    #---test ability to get remarks from user after protocol ends---#
    enter_remarks(output_data)
    #---test overall run function---#
    #run(dataframe_dict)
    # NOTE uncomment this when ready to run file NOTE utils.save_output(output_data, outputfile)


#---helper functions (will be moved into utils once their function is solidified, then into a class for this test in general)---#


def get_acid_volumes(data) -> list:
    '''
    given a csv containing the input data for a solubility test,
    calculates the volumes of acid (in mL) necessary to create a
    given molarity solution.
    '''
    salt_molar_mass = data['molar mass (mg)'][0]
    salt_mass_in_vial = data['mass in vial'][0]

    moles_salt = float(salt_mass_in_vial) / float(salt_molar_mass)

    molarity_grad = [1, 0.8, 0.5, 0.3]
    acid_volumes = [moles_salt / molarity for molarity in molarity_grad]
    

    print(f'{acid_volumes=}')
    return acid_volumes

def assign_spots(data,ingredient) -> dict:
    ''' 
    given a dictionary of information about salts
    and acids in use, assign locations to each of them
    (as of now, salts will be inside of heater & shaker,
    acid stored elsewhere). As of 3/13/24 going to assume the given piece of hardware
    has a 96 well plate on top of it, but the way positions calculated
    can be switched easily
    '''
    if ingredient.lower() == 'salt':
        num_ingredient = len(data['salt'].values())
        print('assigning salt spots...')
        print('ingredient: ', list(data['salt'].values())[0]) # NOTE if multiple salts convert to list instead

    elif ingredient.lower() == 'acid':
        num_ingredient = len(data['acid'].values())   
        print('assigning acid spots...')
        print('ingredient: ', list(data['acid'].values())[0]) # NOTE if multiple acids convert to list instead
    elif ingredient.lower() != 'acid' and ingredient.lower() != 'salt':
        raise AssertionError('specify whether adding acids or salts!')

    print(f'{num_ingredient=}')
    row_map = {1: 'A', 2:'B', 3:'C', 4:'D', 5:'E', 6:'F', 7:'G', 8:'8'}
    shaker_positions = {num+1:'' for num in range(num_ingredient)}

    for i in range(1,num_ingredient+1): # TODO switch this to enumerating through dictionary so users can read off the names/formulae directly instead of 'salt 1'
        vial_letter = row_map[int(i / 12) if int(i/12) != 0 else 1]
        vial_number = i % 12

        shaker_positions[i] = f'{vial_letter}{vial_number}'

    print('Dictionary of positions: ', shaker_positions)
    return shaker_positions

def add_acid(data, protocol, pipette, heater_shaker) -> None: # NOTE can either add protocol:protocol_api... here or put all of these functions in a huge run function
    '''
    given a dictionary containing CSV information, pulls out the volume of acid to be placed
    in each vial, as well as the locations of the acids and salts. to be visited
    '''
    acid_locations = assign_spots(data,'acid')
    salt_locations = assign_spots(data, 'salt')

    acid_volumes = get_acid_volumes(data)
    if max(acid_volumes) > 1000: #NOTE this might not be necessary
        raise AssertionError('pipette tips can only hold maximum of 1000uL')
    

    # NOTE the order of acid volumes corresponds to the molarities in decreasing orders
    for location in list(acid_locations.values()):
        print('acid location(s): ', location)
        protocol.pause(f'is there an acid located at {location}?') #NOTE uncomment this when time to run code

    protocol.pause('are you ready to begin dispensing acids?')

    pipette.pick_up_tip()
    for idx, vial in enumerate(salt_locations.values()):
        acid_vol = acid_volumes[idx]
        pipette.aspirate(acid_vol,list(acid_locations.values())[0])
        pipette.dispense(acid_vol, heater_shaker[vial])
    pipette.drop_tip() # NOTE need to pick up and drop the tips as necessary

def heat_and_shake(heater_shaker,protocol) -> None:
    heater_shaker.set_and_wait_for_temperature(100)
    protocol.delay(minutes=15)
    heater_shaker.deactivate_heater()

    heater_shaker.set_and_wait_for_shake_speed(500)
    protocol.delay(minutes=3)
    heater_shaker.deactivate_shaker()

def enter_remarks(dataframe) -> None:
    remarks = [0 * len(dataframe)]

    for row in range(len(dataframe)):
        remarks[row] = input('Was this mixture soluble? ')

    dataframe['remarks'] = remarks
    print(dataframe) # you'd then save the file to the directory

def run(data, protocol: protocol_api.ProtocolContext) -> None:
    plate = protocol.load_labware("<INSERT PLATE NAME HERE>",location="INSERT LOCATION ON DECK HERE")
    heater_shaker = protocol.load_module('heaterShakerModuleV1', location=4)

    tiprack = protocol.load_labware("opentrons_96_tiprack_1000ul",location="8")
    
    pipette = protocol.load_instrument("p1000_single_gen2",mount="right",tip_racks=[tiprack])

    
    add_acid(data, protocol, pipette, heater_shaker)
    heat_and_shake(heater_shaker,protocol)
    enter_remarks(Pandas.DataFrame.from_dict(data))
    protocol.pause('Enter remarks on laptop')
    #NOTE NOTE NOTE should I heat the heater-shaker at the start of the protocol or after the acids have been added?


    


if __name__ == '__main__':
    cur_dir = Path(os.getcwd())
    input_dir = 'inputs/input.csv'
    output_dir = 'output/output.csv'

    main(cur_dir,input_dir,output_dir)