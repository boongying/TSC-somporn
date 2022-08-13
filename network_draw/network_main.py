from network_draw.network_functions import *
import matplotlib.pyplot as plt

WIDTH, HEIGHT = 600, 600

#Input parameters
input_params =  {'NUM_HORIZ': 4,             #Num. roads
                'NUM_VERTI': 4,             #Num. roads
                'MARGIN_TO_CENTRE': 0.2,    #Dimensioning
                'MARGIN_TO_PLOTEDGE': 0.05, #Dimensioning
                'HALF_ROADWIDTH':0.025,     #Dimensioning
                'BG_COLOUR' : (240/255, 240/255, 240/255, 1.00),#Background colour
                'LINE_COLOUR' : (40/255, 40/255, 40/255, 1.00),#Line colour
                'INT_COLOUR' : (109/255, 82/255, 66/255, 0.45),#Intersection shading
                'OUT_COLOUR' : (87/255, 137/255, 87/255, 0.45),#Outer node shading
                'ART_COLOURMAP': plt.cm.gnuplot} #Arterial plot pyplot colormap

#Meta parameters
horiz_pos = list(np.linspace(input_params['MARGIN_TO_CENTRE'], 1-input_params['MARGIN_TO_CENTRE'], input_params['NUM_HORIZ']))
verti_pos = list(np.linspace(input_params['MARGIN_TO_CENTRE'], 1-input_params['MARGIN_TO_CENTRE'], input_params['NUM_VERTI']))

horiz_pos_full = [input_params['MARGIN_TO_PLOTEDGE']] + horiz_pos + [1-input_params['MARGIN_TO_PLOTEDGE']]
verti_pos_full = [input_params['MARGIN_TO_PLOTEDGE']] + verti_pos + [1-input_params['MARGIN_TO_PLOTEDGE']]

meta_params = {'HORIZ_POS': horiz_pos,
              'VERTI_POS': verti_pos,
              'HORIZ_POS_FULL': horiz_pos_full,
              'VERTI_POS_FULL': verti_pos_full}



with cairo.SVGSurface("./network_draw/example.svg", WIDTH, HEIGHT) as surface:
    ctx = cairo.Context(surface)

    ctx.scale(WIDTH, HEIGHT)  # Normalizing the canvas
    colour = input_params['BG_COLOUR']
    main_pat = cairo.SolidPattern(colour[0], colour[1], colour[2], colour[3])

    ctx.rectangle(0, 0, 1, 1)  # Rectangle(x0, y0, x1, y1)
    ctx.set_source(main_pat)
    ctx.fill()
    
    draw_network(ctx, input_params, meta_params)
    shade_intersection(ctx, input_params, meta_params)
    label_intersection(ctx, input_params, meta_params, position = 'out_corner') #3 options 'centre', 'in_corner' and 'out_corner'
    shade_outer_nodes(ctx, input_params, meta_params)
    label_outer_nodes(ctx, input_params, meta_params, position = 'out_middle')#3 options 'centre', 'in_rim' and 'out_middle'
    draw_edge_label(ctx, input_params, meta_params)

    arteries = [['0_1','1_1','1_2','1_3','1_4','0_4'],
                ['2_3','2_4','3_4','4_4','4_3','3_3','3_2','2_2','2_1','3_1','4_1','4_2','5_2']]
    draw_arteries(ctx,arteries, input_params, meta_params)
        