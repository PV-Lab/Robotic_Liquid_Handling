# library for utility functions
import pandas as pd
import os

class utils:
    def __init__(self):
        pass

    def read_input(self, inputfile):
        input_data = pd.read_csv(inputfile)
        print(input_data)
        return input_data

    def create_output(self, input_data):
        output_data = input_data.copy()
        print(output_data)
        return output_data
    
    def save_output(self, output_data, outputfile):
        old_output = pd.read_csv(outputfile)
        updated_output = pd.concat([old_output, output_data], ignore_index=True)
        updated_output.to_csv(outputfile, index=False)