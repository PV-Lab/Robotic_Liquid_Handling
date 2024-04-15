# import utils
# import os
# from pathlib import Path


# inputfile = Path('C:\Users\emhut\Desktop\MIT\AMLS UROP\OT-2 Protocols\Live_Robotic_Liquid_Handling\df_all.csv')
# input_data = utils.read_input(inputfile)

stock_soln_A = 'Cs1Br1'
stock_soln_B = 'Pb1Br2' # NOTE THE WAY IT IS CURRENTLY IMPLEMENTED EVERY ELEMENT MUST HAVE A NUMBER CORRESPONDING TO IT

example_mix = 'Cs1Pb1Br4'


def parse_formula(formula):
    '''
    expects:
        formula: str representing formula (e.g. Ax1By2Cz3)
    returns:
        dictionary mapping individual elements to their number in formula
    '''
    element = ''
    elements = []
    for letter in formula:
        
        element += letter
        if letter.lower() == letter:
            elements.append(element)
            element = ''
    # every other entry in the list is the ratio 
    elem_map = {}
    for elem, ratio in zip([elements[idx] for idx in range(0,len(elements),2)], [elements[idx] for idx in range(1,len(elements),2)]):
        elem_map[elem] = int(ratio)
    print(f'{formula=}')
    print(f'{elem_map=}')
    print(30*'-')
    return elem_map
        
form_A = parse_formula(stock_soln_A)
form_B = parse_formula(stock_soln_B)
desired = parse_formula(example_mix)

def check_manufacturability(soln_A, soln_B, target):
    '''
    expects:
        soln_A: dictionary from parse_formula for stock solution A
        soln_B: dictionary from parse_formula for stock solution B
        target: dictionary from parse_formula for the desired mixture
    returns:
        True/False based on whether target can be made from soln_A and soln_B
    '''
    
    overlap_check = False
    A_check = False 
    B_check = False

    for elem, num in target.items():
        if elem in soln_A and elem in soln_B:
            if soln_A[elem] + soln_B[elem] == num:
                overlap_check = True
                print('the common element sums to what is needed')
        elif elem in soln_A and elem not in soln_B:
            if soln_A[elem] == num:
                print('the element only found in A is in the right proportion')
                A_check = True
        elif elem in soln_B and elem not in soln_A:
            if soln_B[elem] == num:
                print('the element only found in B is in the right proportion')
                B_check = True

    if A_check and B_check and overlap_check:
        target_str = ''.join(map(str, target.items()))
        print(f'{"".join("".join(map(str, target.items())))} can be made from {"".join("".join(map(str, form_A.items())))} and {"".join("".join(map(str, form_B.items())))} in a 1:1 ratio')
        print(30 * '-')
        return True
    else:
        print(f'{"".join("".join(map(str, target.items())))} can NOT be made from {"".join("".join(map(str, form_A.items())))} and {"".join("".join(map(str, form_B.items())))} in a 1:1 ratio')

print(check_manufacturability(form_A, form_B, desired))
