# TODO IMPLEMENT FUNCTIONALITY FOR WORKING WITH MODULES LIKE THE TEMPERATURE MODULE AND HEATER SHAKER
from opentrons import protocol_api

metadata = {
    "protocolName":"Example Higher Level Abstraction of Code",
    "author":"Evan Hutchinson",
    "description":"Test a more object oriented way to write the code for protocols.",
    "apiLevel": "2.16",
}

def give_me_spots(num_ingredient):
    row_map = {1: 'A', 2:'B', 3:'C', 4:'D', 5:'E', 6:'F', 7:'G', 8:'8'}
    shaker_positions = {} # TODO, in line with keeping track of written names instead of numerical titles of each
    # will need to switch the logic of how this dictionary is initialized

    for i in range(1,num_ingredient+1): # TODO switch this logic around once it comes time to calculate with multiple salts. 
        vial_letter = row_map[int(i / 12) if int(i/12) != 0 else 1]
        vial_number = i % 12
        
        shaker_positions[i] = f'{vial_letter}{vial_number}' # NOTE if you switch from keeping track of acids numerically to keeping track of them by name, the logic for how you
        # calculate the corresponding acid volume needs to change

    #print('Dictionary of positions: ', shaker_positions)
    return shaker_positions 

print('testing spot assignment')
print(give_me_spots(22))

def run(protocol: protocol_api.ProtocolContext,data=None) -> None:
        
    LABWARE = {
        '1mL_pipette':'p1000_single_gen2',
        'microtiter_plate':'nest_96_wellplate_200ul_flat', # NOTE check that max volume is indeed 200uL
        '6_tube_tuberack':'opentrons_6_tuberack_falcon_50ml_conical',
        'opentrons_tiprack':'opentrons_96_tiprack_1000ul',
    }

    class Pipette:
        def __init__(self,tip_type,side, tip_rack,rack_location) -> None:
            '''
            load the pipette into the opentrons software.
            Expects: 
                type: string detailing the pipette name 
                side: string detailing left or right side
                tip_rack: string detailing the type of tiprack in use
            '''
            self.tiprack = protocol.load_labware(LABWARE[tip_rack],str(int(rack_location)))
            self.pipette = protocol.load_instrument(LABWARE[tip_type],mount=side,tip_racks=[self.tiprack]) # NOTE identify the tiprack
            self.rack_location = rack_location

        
        def dispense_volume(self,volume,source, destination,max_volume=2000) -> None:
            # TODO NEED TO ADD A FUNCTION FOR AUTOMATICALLY LOADING LABWARE CLASS  
            '''
            aspirate a specified volume of solution (in uL) at a given location. 
            
            Expects:
                volume: int or float representing volume in uL
                source: a Solution or StockSolution object whose location will be read off
                desitination: a Powder, Labware, or Solution object whose location will be read off
            '''
            source_location_summary = source.get_location()
            source_deck_location = source_location_summary['deck']
            source_labware_name = LABWARE[source_location_summary['labware']]
            source_spot = source_location_summary['spot']

            source_obj = protocol.load_labware(source_labware_name,location=source_deck_location)
            
            destination_loc_summary = destination.get_location()
            print(f'{destination_loc_summary=}')
            destination_deck_location = destination_loc_summary['deck']
            destination_labware_name = LABWARE[destination_loc_summary['name']]
            if isinstance(destination, Plate):
                destination_spot = 'A1' # TODO switch from this being hardcoded 
            else:
                destination_spot = destination_loc_summary['spot']

            destination_obj = protocol.load_labware(destination_labware_name, location=destination_deck_location)

            if volume >= max_volume: # NOTE make sure this is more nuanced than just a max volume number
                raise Exception(f'maximum volume of labware is {max_volume}')
            else:            
                self.pipette.pick_up_tip(self.tiprack)
                self.pipette.aspirate(volume, source_obj[source_spot].center())
                self.pipette.dispense(volume, destination_obj[destination_spot].center())
                
        
    class StockSolution: 
        def __init__(self, deck, labware, spot, concentration,name) -> None:
            '''
            initializes a solution with information about where it is on the deck.
            Pass in the deck slot as an int or str
            '''
            self.location = {'deck':str(int(deck)), 'labware': labware, 'spot':str(spot),}
            self.concentration = concentration
            self.name = name

        def get_location(self) -> dict:
            return self.location
        
        def set_location(self, deck, labware, spot) -> None:
            self.location = {'deck':str(int(deck)), 'labware': labware, 'spot':str(int(spot)),}
        
        
    class Powder:
        def __init__(self, deck, labware, spot, molar_mass) -> None: # NOTE maybe I switch this to mass in vial?
            '''
            initializes a powder with information about where it is on the deck.
            Pass in the deck slot as an int or str
            '''
            self.location = {'deck':str(int(deck)), 'labware': labware, 'spot':str(int(spot)),}
            self.molar_mass = molar_mass

    class Plate:
        def __init__(self,name, deck) -> None:
            '''
            initializes the well plate with its location and its name
                deck: int or str representing the slot on the opentrons deck this is in.
            '''
            self.location = deck
            self.name = name
            self.apiName = LABWARE[name]
            
            # protocol.load_labware(self.apiName, self.location)

            if self.name == 'microtiter_plate':
                self.spots = {f'{letter}{number}':None for letter in 'ABCDEFGH' for number in range(1,13)}

        def get_location(self):
            return {'deck':self.location, 'name':self.name, } # TODO ADD MORE INFO HERE!!!
            
    class Solution(StockSolution):
        id = 0
        
        def __init__(self, deck, labware, spot, concentration, name) -> None:
            Solution.id += 1
            super().__init__(deck, labware, spot, concentration, name)


    pipette = Pipette('1mL_pipette','right','opentrons_tiprack',1)
    microtiter = Plate('microtiter_plate',6)
    HBr = StockSolution(4, '6_tube_tuberack', 'A1', 0.47, 'Hbr')
    pipette.dispense_volume(200, HBr, microtiter)

    
