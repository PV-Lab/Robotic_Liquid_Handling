import pandas as pd
import numpy as np

from opentrons import protocol_api

# All mass in mg
# All molar mass in g/mol
# All volumes in mL
# All molarities in mols/L
# All molar quantities in mmols

metadata = {
    "protocolName":"Two-stock nanocrystal synthesis using Vial Class",
    "author":"Otto Beall",
    "description":"Create a series of materials from 2 stock solutions",
    "apiLevel": "2.16",
}

LABWARE = {
        '1mL_pipette':'p1000_single_gen2',
        'microtiter_plate':'nest_96_wellplate_200ul_flat', # NOTE check that max volume is indeed 200uL
        '6_tube_tuberack':'opentrons_6_tuberack_falcon_50ml_conical',
        'opentrons_tiprack':'opentrons_96_tiprack_1000ul',
}


manual_material_dict =  {'composition': {0: 'Cs2Pb5Br12', 1: 'Cs1Pb2Br5', 2: 'Cs2Pb3Br8', 3: 'Cs3Pb4Br11', 4: 'Cs1Pb1Br3', 5: 'Cs4Pb3Br10', 6: 'Cs3Pb2Br7', 7: 'Cs5Pb3Br11', 8: 'Cs2Pb1Br4', 9: 'Cs5Pb2Br9', 10: 'Cs3Pb1Br5', 11: 'Cs7Pb2Br11', 12: 'Cs4Pb1Br6'}, 'Atoms': {0: '[2, 5, 12]', 1: '[1, 2, 5]', 2: '[2, 3, 8]', 3: '[3, 4, 11]', 4: '[1, 1, 3]', 5: '[4, 3, 10]', 6: '[3, 2, 7]', 7: '[5, 3, 11]', 8: '[2, 1, 4]', 9: '[5, 2, 9]', 10: '[3, 1, 5]', 11: '[7, 2, 11]', 12: '[4, 1, 6]'}, 'Ind Charges': {0: '[[1], [2], [-1]]', 1: '[[1], [2], [-1]]', 2: '[[1], [2], [-1]]', 3: '[[1], [2], [-1]]', 4: '[[1], [2], [-1]]', 5: '[[1], [2], [-1]]', 6: '[[1], [2], [-1]]', 7: '[[1], [2], [-1]]', 8: '[[1], [2], [-1]]', 9: '[[1], [2], [-1]]', 10: '[[1], [2], [-1]]', 11: '[[1], [2], [-1]]', 12: '[[1], [2], [-1]]'}, 'ratio_1': {0: 2, 1: 1, 2: 2, 3: 3, 4: 1, 5: 4, 6: 3, 7: 5, 8: 2, 9: 5, 10: 3, 11: 7, 12: 4}, 'ratio_2': {0: 5, 1: 2, 2: 3, 3: 4, 4: 1, 5: 3, 6: 2, 7: 3, 8: 1, 9: 2, 10: 1, 11: 2, 12: 1}, 'A:B Ratio': {0: 0.4, 1: 0.5, 2: 0.6666666666666666, 3: 0.75, 4: 1.0, 5: 1.3333333333333333, 6: 1.5, 7: 1.6666666666666667, 8: 2.0, 9: 2.5, 10: 3.0, 11: 3.5, 12: 4.0}}

mat_to_make = pd.DataFrame(manual_material_dict)

# mat_to_make = pd.read_csv('inputs/materials_to_make_CsPbBr.csv')
# mat_to_make['A:B Ratio'] = mat_to_make['ratio_1']/mat_to_make['ratio_2']
# mat_to_make = mat_to_make.sort_values(by='A:B Ratio')
# mat_to_make = mat_to_make.reset_index(drop=True)
mat_dict = mat_to_make.to_dict()
print(mat_dict)
num_mats = len(mat_to_make)
print(40 * '-')
print('Materials to make: \n',mat_to_make)
print('Dictionary Form \n',mat_dict)
print(40*'-')
print(f'{num_mats=}')

a_b_ratio = mat_dict['A:B Ratio']
print(a_b_ratio)

well_volume = 1

A_vols = []
B_vols = []
for part_a, part_b in zip(mat_to_make['ratio_1'], mat_to_make['ratio_2']):
    A_vols.append(well_volume*part_a/(part_a+part_b))
    B_vols.append(well_volume*part_b/(part_a+part_b))


def run(protocol:protocol_api.ProtocolContext) -> None:
    tiprack = protocol.load_labware(LABWARE['opentrons_tiprack'],6)
    pipette = protocol.load_instrument(LABWARE['1mL_pipette'],mount='right',tip_racks=[tiprack])
    tuberack = protocol.load_labware(LABWARE['6_tube_tuberack'],9)  
    heater_shaker = protocol.load_module('heaterShakerModuleV1', location='4') # NOTE placed in spot 9 so less splash hazard
    heater_shaker_plate = heater_shaker.load_labware('opentrons_24_aluminumblock_generic_2ml_screwcap')
    heater_shaker.close_labware_latch()
    dropcast_holder = protocol.load_labware('ottobeall_15_wellplate_100ul',2)
    stock_molarity = 1
    stock_volume = 10
    acid_molarity = 9

    A_stock = Vial({'Cs+':stock_molarity*stock_volume,'Ac-':stock_molarity*stock_volume,'H+':acid_molarity*stock_volume,'Br-':acid_molarity*stock_volume},
                    {'H2O':stock_volume},
                    tuberack,'A1',max_volume=90,complete=True)
    B_stock = Vial({'Pb2+':stock_molarity*stock_volume,'Br-':(stock_molarity+acid_molarity)*stock_volume,'H+':acid_molarity*stock_volume},
                    {'H2O':stock_volume},
                    tuberack,'A2',max_volume=90,complete=True)
    
    product_vials = []

    for i in range(len(A_vols)):
        product_vials.append(Vial({},{},heater_shaker_plate,i,max_volume = 5))
    
    pipette.pick_up_tip()
    for i in range(len(product_vials)):
        product_vials[i].add_liquid(A_stock,A_vols[i],pipette,new_tip='never')
    pipette.drop_tip()
    pipette.pick_up_tip()
    for i in range(len(product_vials)):
        product_vials[i].add_liquid(B_stock,B_vols[i],pipette,new_tip='never')
        product_vials[i].completed()
    pipette.drop_tip()
    for i in range(len(product_vials)):
        protocol.pause(product_vials[i].__str__())

    drops = []
    for i in range(len(product_vials)):
        drops.append(Vial({},{},dropcast_holder,i,max_volume = 0.1))   
    for i in range(len(product_vials)):
        drops[i].add_liquid(product_vials[i],0.01,pipette)

class Vial:
    ''' 
    A class that tracks the contents and location of a vial.
    '''
    def __init__(self,solute_mmols:dict,solvent_vols:dict,labware,location,max_volume:float,complete = False):
        '''
        Initializes a new Vial object

        Parameters
        ----------
        solute_mmoles : dict
            A dictionary mapping each ion ('H+' , 'Pb2+' , 'Cl-' ...) to a quantity in mmols
            For clarity use IUPAC chemical names or common abbreviations (eg. MA for Methylammonium) followed by the charge ('+','2+','-','2-'...etc)
        solvent_vols : dict
            A dictionary mapping each solvent ('H2O' , 'DMF', 'DMSO' ...) to a volume in mL
        labware
            An opentrons labware object representing the labware that the vial is contained in
        location
            An integer or string representing the vial's position within the labware. 
            A numerical index (0,1,2...) or letter-number pair ('A1','A2','B1'...) is acceptable.
        max_volume : float
            Maximum volume of the vial in mL.
        complete : bool, defaults to False
            A boolean representing whether the Vial is complete (no more ingredients will be added to it).

        )
        '''
        self.solute_mmols = solute_mmols
        self.solvent_vols = solvent_vols
        self.labware = labware
        self.location = location
        self.max_volume = max_volume
        self.complete = complete
        if self.get_volume()>max_volume:
            raise Exception("Volume in vial exceeds maximum")
        if(complete):
            self.complete_volume = self.get_volume()
            if self.complete_volume <= 0:
                raise Exception("Vial cannot be complete without addition of liquid.")
            self.fraction_left = 1
        else:
            self.complete_volume = None
            self.fraction_left = None

    def add_liquid(self,other_solution,volume,pipette,new_tip='always',source_z_offset=None):
        '''
        Adds liquid from another vial

        Parameters
        ----------
        other_solution
            Vial object representing the source of the added liquid.
        volume
            Volume of other solution to be added to the vial in mL.

        '''
        #Only proceeds if this Vial has NOT been marked as complete and the other Vial has been marked as complete.
        if(self.is_complete()):
            raise Exception("Attempted to add to a solution that was marked as complete.")
        
        elif(other_solution.is_complete()):
            #Reduces the remaining fraction of the other solution.
            other_solution.extract(volume)
            volume_fraction = volume / other_solution.get_complete_volume()
            for ion in other_solution.get_complete_solute_mmols():
                if ion in self.solute_mmols:
                    self.solute_mmols[ion] += other_solution.get_complete_solute_mmols()[ion]*volume_fraction
                else:
                    self.solute_mmols[ion] = other_solution.get_complete_solute_mmols()[ion]*volume_fraction
            for solvent in other_solution.get_complete_solvent_vols():
                if solvent in self.solvent_vols:
                    self.solvent_vols[solvent] += other_solution.get_complete_solvent_vols()[solvent]*volume_fraction
                else:
                    self.solvent_vols[solvent] = other_solution.get_complete_solvent_vols()[solvent]*volume_fraction
            if(self.get_volume() > self.max_volume):
                raise Exception("Volume in vial exceeds maximum.")
            if(source_z_offset == None):
                pipette.transfer(volume*1000,other_solution.get_labware().wells(other_solution.get_location()).bottom(z=source_z_offset),self.labware.wells(self.location),new_tip=new_tip)
            else:
                pipette.transfer(volume*1000,other_solution.get_labware().wells(other_solution.get_location()),self.labware.wells(self.location),new_tip=new_tip)
        else:
            raise Exception("Attempted to extract from a solution that was not complete. (Use is_complete() to complete filling a vial)")

    def get_volume(self):
        '''
        Gets the current volume contained in the vial.
        '''
        output = 0
        for solvent in self.solvent_vols:
            output += self.solvent_vols[solvent]
        return output
    
    def get_complete_volume(self):
        '''
        Gets the total volume of the Vial when it was first completed.
        '''
        if(self.is_complete):
            return self.complete_volume
        else:
            raise Exception("Attempted to get the complete volume of a vial not marked as complete.")
    
    def extract(self,volume):
        '''
        Decreases the fraction of the total solution remaining in the vial.
        '''
        if volume < self.complete_volume * self.fraction_left:
            self.fraction_left -= volume/self.complete_volume
        else:
            raise Exception(f"Attempted to extract greater than remaining volume in vial. Total volume: {self.complete_volume} mL. Remaining Fraction: {self.fraction_left}")
        
    def get_molarities(self):
        '''
        Returns a dictionary of molarities (mols/L) for each of the ions in the solution.
        '''
        volume = self.get_volume()
        output = {}
        for solute in self.solute_mmols:
            output[solute] = self.solute_mmols[solute]/volume
        return output

    def complete(self):
        '''
        Changes the Vial's status to complete, indicating that nothing more will be added to it.
        '''
        self.complete_volume = self.get_volume()
        if self.complete_volume <= 0:
            raise Exception("Vial cannot be complete without addition of liquid.")
        self.fraction_left = 1
        self.complete = True

    def get_complete_solute_mmols(self):
        '''
        Returns a dictionary mapping each ion to its quantity in the Vial when first completed.
        '''
        return self.solute_mmols
    
    def get_complete_solvent_vols(self):
        '''
        Returns a dictionary mapping each solvent to its volume when the Vial was first completed.
        '''
        return self.solvent_vols
    
    def is_complete(self):
        '''
        Returns a boolean indicating whether the Vial has been marked as complete.
        '''
        return self.complete
    
    def get_labware(self):
        '''
        Returns the labware where the Vial is located.
        '''
        return self.labware
    
    def get_location(self):
        '''
        Returns the Vial's location within its specified labware. A numerical index (0,1,2...) or letter-number pair ('A1','A2','B1'...) is acceptable.
        '''
        return self.location
    def __str__(self):
        output = "Vial containing the following chemicals:  "
        for solute in self.get_molarities():
            output += f"{solute} : {str(self.get_molarities()[solute])} mols/L, "
        return output