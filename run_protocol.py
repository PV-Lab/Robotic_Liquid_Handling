from pathlib import Path
import solubility_testing
import material_discovery
import utils
import pymatgen as mg
import pandas as pd

# Name of the protocol
run_protocol = "Material Discovery" #Material Discovery ; Solubitlity_testing ; Material Optimization


if run_protocol == 'Material Discovery':
    no_of_elems =3
    elems = 'CsPbBr'
    print(elems)
    library = Path("./Data/material_candidates.csv")
    material_candidates = utils.read_input(library)
    material_discovery.main(material_candidates, no_of_elems, elems)