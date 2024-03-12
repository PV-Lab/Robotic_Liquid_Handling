# user editable file to run solubility testing
import solubility_testing
from pathlib import Path
import os

cur_dir = Path(os.getcwd())
input_dir = 'inputs/input.csv'
output_dir = 'output/output.csv'

solubility_testing.main(cur_dir, input_dir, output_dir)