# import matplotlib.pyplot as plt
from opentrons import protocol_api
from opentrons import types 
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

LABWARE = {
        '1mL_pipette':'p1000_single_gen2',
        'microtiter_plate':'nest_96_wellplate_200ul_flat', # NOTE check that max volume is indeed 200uL
        '6_tube_tuberack':'opentrons_6_tuberack_falcon_50ml_conical',
        'opentrons_tiprack':'opentrons_96_tiprack_1000ul',
    }

metadata = {
    "protocolName":"Glass Slide Positioning",
    "author":"Evan Hutchinson",
    "description":"Test the locations of points on the glass slides",
    "apiLevel": "2.16",
}


def run(protocol:protocol_api.ProtocolContext):
    glass_slide = protocol.load_labware(LABWARE['microtiter_plate'], 2)
    
    tiprack = protocol.load_labware("opentrons_96_tiprack_1000ul",location="8")
    #----load in pipette(s) here----#
    pipette = protocol.load_instrument("p1000_single_gen2",mount="right",tip_racks=[tiprack])
    drop_points = glass_slide_coordinates(3,2, 1, 1.5)

    def drop_on_glass(points, volume):
        '''
        expects:
            points: a list of x,y tuples 
            volume (uL) of liquid to   
        '''
        pipette.pick_up_tip(tiprack['A1'])

        for coord in points[:1]:
            x_coord, y_coord = coord
            pipette.move_to(types.Location(types.Point(x=x_coord,y=y_coord,z=20),glass_slide))
            protocol.pause('look good?')
    
    drop_on_glass(drop_points,0)

def glass_slide_coordinates(length, width, border, spacing):
    '''
    return a set of x,y coordinates corresponding to locations on a 
    glass slide for drop casting

    expects:
        -length (inch) of plate along horizontal axis
        -width (inch) of plate along vertical axis
        -border (cm) of how much space to be left on all sides
        spacing (cm) of space between droplets
    '''
    length_mm = length * 25.4
    width_mm = width * 25.4
    border_mm = border * 10
    spacing_mm = spacing * 10

    xy_coords = []
    x0, y0 = (border_mm, border_mm)

    #NOTE implementation 1 using a for loop and casting everything to ints
    # for x in range(0, int(length_mm - 2 * spacing_mm), int(spacing_mm)):
    #     for y in range(0, int(width_mm - 2 * spacing_mm), int(spacing_mm)):
    #         xy_coords.append((x0 + x, y0 + y))
    
    # print('coords via for loops: ', xy_coords)
    # return xy_coords

#NOTE implementation 2 using a while loop 
    x = border_mm
    y = border_mm

    xcoords = []
    ycoords = []
    print('length: ', length_mm)
    print('width: ', width_mm)
    while x <= (length_mm - border_mm):
        xcoords.append(x)
        print('x: ', x)
        x += spacing_mm
        
    
    while y <= (width_mm - border_mm):
        ycoords.append(y)
        print('y: ', y)
        y += spacing_mm

    for x in xcoords:
        for y in ycoords:
            xy_coords.append((x,y))
    print('coords via while loops: ', xy_coords)

    
    x_points, y_points = zip(*xy_coords)
    rectangle = matplotlib.patches.Rectangle(xy=(x,y),
                                     width = length_mm, height = width_mm,
                                     color ='red')
    
    left_lim = np.linspace(0,length_mm,100)
    right_lim = np.linspace(0, width_mm,100)
    left_vert = np.zeros(100)
    right_vert = [num * length_mm for num in np.ones(100)]
    lower_horz = np.zeros(100)
    upper_horz = [num * width_mm for num in np.ones(100)]



    # plt.plot(left_vert, left_lim)
    # plt.plot(right_vert, right_lim)
    # plt.plot(lower_horz, left_lim)
    # plt.plot(upper_horz, right_lim)
    # plt.scatter(x_points,y_points)
    # plt.xlim(left=0, right=length_mm)
    # plt.ylim(bottom=0, top=width_mm)
    # plt.show()

    points = sorted(xy_coords, key=lambda tup: tup[0])
    print(xy_coords)
    return points


# glass_slide_coordinates(6,4,1,1.5)
glass_slide_coordinates(3, 2, 1, 1.5)
# glass_slide_coordinates(11, 11, 1, 1)