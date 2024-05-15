# All mass in mg
# All molar mass in g/mol
# All volumes in mL
# All molarities in mols/L
# All molar quantities in mmols
import os
import pandas as Pandas

from opentrons import protocol_api
from opentrons import types

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