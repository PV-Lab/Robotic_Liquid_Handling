import opentrons.simulate 
protocol_file = open("test_dispensing.py")    
opentrons.simulate.simulate(protocol_file)