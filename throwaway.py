increment = 0

for idx, letter in enumerate("ABCDEFGH"):
    for num in range(1, 13):        
        well = f'{letter}{num}' 
        gain = 2       
        print(f"{well=} | forward quantity = {(95 - increment) * gain * 1.05} | reverse quantity = {increment * gain* 1.06}") 
        increment += 1 
        

