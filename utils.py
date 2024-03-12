# library for utility functions
import pandas as pd
from pathlib import Path

def read_input(inputfile : Path) -> pd.DataFrame:
    input_data = pd.read_csv(inputfile)
    print(input_data)
    return input_data

def create_output(input_data : pd.DataFrame) -> pd.DataFrame:
    output_data = input_data.copy()
    print(output_data)
    return output_data

def save_output(output_data :pd.DataFrame, outputfile : Path) -> None:
    old_output = pd.read_csv(outputfile)
    updated_output = pd.concat([old_output, output_data], ignore_index=True)
    updated_output.to_csv(outputfile, index=False)