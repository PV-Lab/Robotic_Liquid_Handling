# import utils # NOTE had to comment this out because opentrons doesn't know what utils is 
import os
import pandas as Pandas


from pathlib import Path
from opentrons import protocol_api
from opentrons import types



metadata = {
    "protocolName":"Solubility Testing",
    "author":"Evan Hutchinson",
    "description":"Evaluate the solubility of different mixtures by making a molarity gradient & seeing what dissolves",
    "apiLevel": "2.16",
}

requirements = {"robotType": "OT-2",}


molarity_grad = [1, 0.8, 0.5, 0.3] # NOTE for now these will be manually measured & input into the vials?

# NOTE this is an example csv file which would be printed in using the input_data variable, then copy pasted into the protocol like so
# to avoid the Opentrons throwing errors about not knowing what the imported files are 
DATA = {'date': {0: 3122024}, 'owner': {0: 'basitadas'}, 'salt': {0: 'Lead iodide'}, 'formula': {0: 'PbI2'}, 'barcode': {0: 203409}, 
        'purity': {0: 99.9999}, 'molar mass (mg)': {0: 461.01 * 1000}, 'mass in vial': {0: 230.51}, 'acid': {0: 'Hydrogen bromide'}, 
        'formula.1': {0: 'HBr2'}, 'barcode.1': {0: 504309}, 'concentration': {0: '47%'}, 'volume (ml)': {0: 1}, 'remarks': {0: None}} # NOTE none is 'nan' in actual CSV

def main(cur_dir, input_dir, output_dir):
    # read input file
    inputfile = Path(cur_dir/input_dir)
    outputfile = Path(cur_dir/output_dir)
   
    input_data = utils.read_input(inputfile)
    
    output_data = utils.create_output(input_data)

    #---test how to load it into the database---#
    # dataframe_dict = Pandas.DataFrame.to_dict(output_data)
    dataframe_dict = DATA
    #print(f'{dataframe_dict=}')
    #------------------------------------------#

    #---test assigning spots for salts & acids---#
    assign_spots(dataframe_dict,'salt')
    #--------------------------------------------#

    #---test adding acid into the salt vials---#
    # add_acid(dataframe_dict,protocol)   # NOTE add relevant arguments to fix bugs
    #--------------------------------------------#

    #---test calculating acid volume calculation---#
    get_acid_volumes(dataframe_dict)

    #---test ability to get remarks from user after protocol ends---#
    enter_remarks(output_data)
    #---test overall run function---#
    run(protocol_api.ProtocolContext, DATA)
    # NOTE uncomment this when ready to run file NOTE utils.save_output(output_data, outputfile)


#---helper functions (will be moved into utils once their function is solidified, then into a class for this test in general)---#


def get_acid_volumes(data) -> dict:
    '''
    given a csv containing the input data for a solubility test,
    calculates the volumes of acid (in uL) necessary to create a
    given molarity solution and maps them to a {vial number:volume} dictionary.
    '''
    salt_molar_mass = data['molar mass (mg)'][0]
    salt_mass_in_vial = data['mass in vial'][0]
    print(f'{salt_molar_mass=}')
    # moles_salt = float(salt_mass_in_vial) / float(salt_molar_mass) 
    moles_salt = float(salt_mass_in_vial) / salt_molar_mass  # NOTE it's an arbitrary number in the denominator here so there are no errors with reading from csv for now 

    molarity_grad = [1, 0.8, 0.5, 0.3]
    acid_volumes = [((moles_salt / molarity) * 1000) * 1000 for molarity in molarity_grad] # in uL
    
    output_vols = {idx + 1:volume for idx, volume in enumerate(acid_volumes)}
    print(f'{output_vols=}')
    return output_vols

                
                
    
def assign_spots(data,ingredient='salt') -> dict:
    ''' 
    given a dictionary of information about salts
    and acids in use, assign locations to each of them
    (as of now, salts will be inside of heater & shaker,
    acid stored elsewhere). As of 3/13/24 going to assume the given piece of hardware
    has a 96 well plate on top of it, but the way positions calculated
    can be switched easily
    '''
    if ingredient.lower() == 'salt':
        # num_ingredient = len(data['salt'][0]) # NOTE one ingredient for now, this is also still bugged
        num_ingredient = 4
        #print('assigning salt spots...')
        #print('ingredient: ', DATA['salt'][0]) # NOTE if multiple salts convert to list instead
        

    elif ingredient.lower() == 'acid':
        # #print(data['acid'][0])
        # num_ingredient = len(data['acid'].values()[0])   
        num_ingredient = 1
        #print('assigning acid spots...')
        #print('ingredient: ', DATA['acid'][0]) # NOTE if multiple acids convert to list instead
        
    elif ingredient.lower() != 'acid' and ingredient.lower() != 'salt':
        raise AssertionError('specify whether adding acids or salts!')

    #print(f'{num_ingredient=}')
    row_map = {1: 'A', 2:'B', 3:'C', 4:'D', 5:'E', 6:'F', 7:'G', 8:'8'}
    shaker_positions = {} # TODO, in line with keeping track of written names instead of numerical titles of each
    # will need to switch the logic of how this dictionary is initialized

    for i in range(1,num_ingredient+1): # TODO switch this logic around once it comes time to calculate with multiple salts. 
        vial_letter = row_map[int(i / 6)+1]
        vial_number = i % 6
        
        shaker_positions[i] = f'{vial_letter}{vial_number}' # NOTE if you switch from keeping track of acids numerically to keeping track of them by name, the logic for how you
        # calculate the corresponding acid volume needs to change

    #print('Dictionary of positions: ', shaker_positions)
    return shaker_positions 



def enter_remarks(dataframe) -> None:
    '''
    function for entering remarks about the materials tested.
    requires the user takes a break from monitoring the physical 
    robot & Opentrons app status to enter the results in a vscode or python terminal
    '''
    remarks = [0 * len(dataframe)]

    for row in range(len(dataframe)):
        remarks[row] = input('Was this mixture soluble? ')

    dataframe['remarks'] = remarks
    #print(dataframe) # you'd then save the file to the directory

def run(protocol: protocol_api.ProtocolContext,data=None) -> None:
    tube_rack = protocol.load_labware('opentrons_6_tuberack_falcon_50ml_conical',location='9')
    
    heater_shaker = protocol.load_module('heaterShakerModuleV1', location='4') 
    
    heater_shaker_plate = heater_shaker.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap')
    
    heater_shaker.set_target_temperature(90)
    
    heater_shaker.close_labware_latch()
    tiprack = protocol.load_labware('opentrons_96_tiprack_1000ul',location='6') 
    pipette = protocol.load_instrument('p1000_single_gen2',mount="right",tip_racks=[tiprack])

    
    
    def dispense_vol(volume, source, destination, max_volume=2000) -> None:
        '''
        takes in a single volume in uL and aspirates/dispenses it as necessary. if volume is
        greater than pipette capacity, then aspirate/dispense multiple times until done. 
        Assumes this function will repeatedly be called inside of a loop.
        '''
        
        
        if volume >= 1000 and volume < max_volume:
            num_trips = int(volume // 1000)
            rem = volume - num_trips * 1000

            pipette.transfer(rem, source, destination,new_tip='never')
            for _ in range(num_trips):
                pipette.transfer(1000, source, destination,new_tip='never')
        elif volume >= max_volume:
            protocol.pause(f'max volume of vials is {max_volume}ul. Skipping this vial')
        else:
            pipette.transfer(volume, source, destination, new_tip='never')

    def add_acid() -> None: # NOTE as of now these are all inside of a huge run function, but can pull them out of it later on in development.
        # right now just annoying to keep track of every single labware definition to pass in 
        '''
        given a dictionary containing CSV information, pulls out the volume of acid to be placed
        in each vial, as well as the locations of the acids and salts. to be visited
        '''
        acid_locations = assign_spots(DATA,'acid')  
        salt_locations = assign_spots(DATA, 'salt')

        acid_volumes = get_acid_volumes(DATA)
       
        

        # NOTE the order of acid volumes corresponds to the molarities in decreasing orders
        for acid, location in acid_locations.items():
            
            protocol.pause(f'is there an acid located at {location}?') #NOTE uncomment this when time to run code

        protocol.pause('are you ready to begin dispensing acids?')

        pipette.pick_up_tip()
        for idx, vial in salt_locations.items():

            acid_vol = acid_volumes[idx]
            dispense_vol(acid_vol, tube_rack[acid_locations[1]].center(), heater_shaker_plate[vial].center(),2000)
           
        pipette.drop_tip() # NOTE need to pick up and drop the tips as necessary

 
    
    add_acid()
    # heat_and_shake()
    
    heater_shaker.set_and_wait_for_shake_speed(500)
    protocol.delay(minutes=1)
    heater_shaker.deactivate_shaker()
    heater_shaker.deactivate_heater()

    enter_remarks(Pandas.DataFrame.from_dict(data))
    protocol.pause('Enter remarks on laptop')
    

if __name__ == '__main__':
    cur_dir = Path(os.getcwd())
    input_dir = 'inputs/input.csv'
    output_dir = 'output/output.csv'

    main(cur_dir,input_dir,output_dir)