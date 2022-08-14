import numpy as np
import math
import cairo
from itertools import product

def draw_network(ctx, input_params, meta_params):
    half_roadwidth = input_params['HALF_ROADWIDTH']
    margin_to_plotedge = input_params['MARGIN_TO_PLOTEDGE']
    colour_outline = input_params['LINE_COLOUR']
    colour_road = input_params['BG_COLOUR']
    
    horiz_pos = meta_params['HORIZ_POS']
    verti_pos = meta_params['VERTI_POS']
    #Creating road outlines
    for h in horiz_pos:
        ctx.move_to(h-half_roadwidth, margin_to_plotedge)
        ctx.line_to(h-half_roadwidth, 1-margin_to_plotedge)
        ctx.move_to(h+half_roadwidth, margin_to_plotedge)
        ctx.line_to(h+half_roadwidth, 1-margin_to_plotedge) 
    for v in verti_pos:
        ctx.move_to(margin_to_plotedge, v-half_roadwidth)
        ctx.line_to(1-margin_to_plotedge, v-half_roadwidth)
        ctx.move_to(margin_to_plotedge, v+half_roadwidth)
        ctx.line_to(1-margin_to_plotedge, v+half_roadwidth) 
    ctx.set_source_rgba(colour_outline[0], colour_outline[1],
                        colour_outline[2], colour_outline[3])  # Solid color
    ctx.set_line_width(0.003)
    ctx.stroke()
    
    #Clearing the outlines of conflict areas
    for h in horiz_pos:
        ctx.move_to(h, margin_to_plotedge)
        ctx.line_to(h, 1-margin_to_plotedge)
    for v in verti_pos:
        ctx.move_to(margin_to_plotedge, v)
        ctx.line_to(1-margin_to_plotedge, v)
    ctx.set_source_rgba(colour_road[0], colour_road[1],
                        colour_road[2], colour_road[3])  # Solid color
    ctx.set_line_width(0.047)
    ctx.stroke()

def shade_intersection(ctx, input_params, meta_params):
    half_roadwidth = input_params['HALF_ROADWIDTH']
    margin_to_plotedge = input_params['MARGIN_TO_PLOTEDGE']
    colour = input_params['INT_COLOUR']
    
    horiz_pos = meta_params['HORIZ_POS']
    verti_pos = meta_params['VERTI_POS']
    for h in horiz_pos:
        for v in verti_pos:
            ctx.rectangle(h-half_roadwidth, v-half_roadwidth,
                          margin_to_plotedge, margin_to_plotedge)
            
    pat = cairo.SolidPattern(colour[0], colour[1], colour[2], colour[3])
    ctx.set_source(pat)
    ctx.fill()


def label_intersection(ctx, input_params, meta_params, position = 'out_corner'):
    half_roadwidth = input_params['HALF_ROADWIDTH']
    colour_light = input_params['BG_COLOUR']
    colour_dark = input_params['LINE_COLOUR']
    
    horiz_pos = meta_params['HORIZ_POS']
    verti_pos = meta_params['VERTI_POS']
    
    ctx.select_font_face("Bahnschrift", cairo.FONT_SLANT_NORMAL, 
        cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(half_roadwidth*0.8)

    for i,h in enumerate(horiz_pos, start = 1):
        for j,v in enumerate(verti_pos,start = 1):
            (x, y, width, height, dx, dy) = ctx.text_extents("%d,%d"%(i,j))
            if position == 'centre':
                ctx.set_source_rgba(colour_light[0], colour_light[1],
                                    colour_light[2], colour_light[3])
                ctx.move_to(h-width/1.8, v+height/3)
            elif position == 'in_corner':
                ctx.set_source_rgba(colour_light[0], colour_light[1],
                                    colour_light[2], colour_light[3])
                ctx.move_to(h-width, v+height)
            elif position == 'out_corner':
                ctx.set_source_rgba(colour_dark[0], colour_dark[1],
                                    colour_dark[2], colour_dark[3])
                ctx.move_to(h-2.2*half_roadwidth, v-1.3*half_roadwidth)
            ctx.show_text("%d,%d"%(i,j))

def shade_outer_nodes(ctx, input_params, meta_params):
    half_roadwidth = input_params['HALF_ROADWIDTH']
    margin_to_plotedge = input_params['MARGIN_TO_PLOTEDGE']
    colour = input_params['OUT_COLOUR']
    
    horiz_pos = meta_params['HORIZ_POS']
    verti_pos = meta_params['VERTI_POS']
    
    for h in horiz_pos:
        ctx.move_to(h, margin_to_plotedge)
        ctx.arc(h, margin_to_plotedge, half_roadwidth, 0, 2*math.pi)
        ctx.move_to(h, 1-margin_to_plotedge)
        ctx.arc(h, 1-margin_to_plotedge, half_roadwidth, 0, 2*math.pi)
    for v in verti_pos:
        ctx.move_to(margin_to_plotedge, v)
        ctx.arc(margin_to_plotedge, v, half_roadwidth, 0, 2*math.pi)
        ctx.move_to(1-margin_to_plotedge, v)
        ctx.arc(1-margin_to_plotedge, v, half_roadwidth, 0, 2*math.pi)
        
    pat = cairo.SolidPattern(colour[0], colour[1], colour[2], colour[3])
    ctx.set_source(pat)
    ctx.fill()
    
def label_outer_nodes(ctx, input_params, meta_params, position = 'out_corner'):
    num_horiz = input_params['NUM_HORIZ']
    num_verti = input_params['NUM_VERTI']
    half_roadwidth = input_params['HALF_ROADWIDTH']
    margin_to_plotedge = input_params['MARGIN_TO_PLOTEDGE']
    colour_light = input_params['BG_COLOUR']
    colour_dark = input_params['LINE_COLOUR']
    
    horiz_pos = meta_params['HORIZ_POS']
    verti_pos = meta_params['VERTI_POS']

    ctx.select_font_face("Bahnschrift", cairo.FONT_SLANT_NORMAL, 
        cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(half_roadwidth*0.8)
    for i,h in enumerate(horiz_pos,start = 1):
        (x, y, width, height, dx, dy) = ctx.text_extents("%d,%d"%(i,num_verti+1))
        if position == 'centre':
            ctx.set_source_rgba(colour_light[0], colour_light[1],
                                colour_light[2], colour_light[3])
            ctx.move_to(h-width/2, margin_to_plotedge+0.01)
        elif position == 'in_rim':
            ctx.set_source_rgba(colour_light[0], colour_light[1],
                                colour_light[2], colour_light[3])
            ctx.move_to(h-width*0.9, margin_to_plotedge*1.4)
        elif position == 'out_middle':
            ctx.set_source_rgba(colour_dark[0], colour_dark[1],
                                colour_dark[2], colour_dark[3])
            ctx.move_to(h-2.1*half_roadwidth, margin_to_plotedge/1.25)
        ctx.show_text("%d,%d"%(i,num_verti+1))

        
        (x, y, width, height, dx, dy) = ctx.text_extents("%d,%d"%(i,0))
        if position == 'centre':
            ctx.move_to(h-width/2, 1-margin_to_plotedge+0.01)
        elif position == 'in_rim':
            ctx.move_to(h-width*0.9, 1-margin_to_plotedge/1.6)
        elif position == 'out_middle':
            ctx.move_to(h-2.1*half_roadwidth, 1-margin_to_plotedge*1.25)
        ctx.show_text("%d,%d"%(i,0))
    
    for j,v in enumerate(verti_pos,start = 1):
        (x, y, width, height, dx, dy) = ctx.text_extents("%d,%d"%(0,j))
        if position == 'centre':
            ctx.move_to(margin_to_plotedge-0.016, v+height/3)
        elif position == 'in_rim':
            ctx.move_to(margin_to_plotedge/1.6, v+height)
        elif position == 'out_middle':
            ctx.move_to(margin_to_plotedge/4, v-1.3*half_roadwidth)
        ctx.show_text("%d,%d"%(0,j))
        
        (x, y, width, height, dx, dy) = ctx.text_extents("%d,%d"%(num_horiz+1,j))
        if position == 'centre':
            ctx.move_to(1-margin_to_plotedge-0.016, v+height/3)
        elif position == 'in_rim':
            ctx.move_to(1-margin_to_plotedge*1.4, v+height)
        elif position == 'out_middle':
            ctx.move_to(1-margin_to_plotedge*1.8, v-1.3*half_roadwidth)
        ctx.show_text("%d,%d"%(num_horiz+1,j))

def edge_pos(A,B, meta_params):
    horiz_pos_full = meta_params['HORIZ_POS_FULL']
    verti_pos_full = meta_params['VERTI_POS_FULL']
    
    Ai, Aj = int(A[0]), int(A[-1])
    Bi, Bj = int(B[0]), int(B[-1])
    edge_v = (verti_pos_full[Aj] + verti_pos_full[Bj])/2
    edge_h = (horiz_pos_full[Ai] + horiz_pos_full[Bi])/2
    return edge_h, edge_v



def draw_edge_label(ctx, df_weights, input_params, meta_params):
    num_horiz = input_params['NUM_HORIZ']
    num_verti = input_params['NUM_VERTI']
    half_roadwidth = input_params['HALF_ROADWIDTH']
    colour = input_params['LINE_COLOUR']

    ctx.set_source_rgba(colour[0], colour[1], colour[2], colour[3])
    ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, 
        cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(half_roadwidth/1.2)

    
    adj = np.where(~np.isnan(df_weights.to_numpy()))
    for m,n in zip(adj[0],adj[1]):
        edge_h, edge_v = edge_pos(df_weights.index[m], df_weights.columns[n], meta_params)
        (x, y, width, height, dx, dy) = ctx.text_extents("+%.2f" %df_weights.iloc[m,n]\
                                        if df_weights.iloc[m,n]>0 else "%.2f" %df_weights.iloc[m,n])
        ctx.move_to(edge_h-dx/2, edge_v+height/2)
        ctx.show_text("+%.2f" %df_weights.iloc[m,n] if df_weights.iloc[m,n]>0 else "%.2f" %df_weights.iloc[m,n])
        
def draw_arteries(ctx, arts, input_params, meta_params):
    half_roadwidth = input_params['HALF_ROADWIDTH']
    art_colormap = input_params['ART_COLOURMAP']
    
    horiz_pos_full = meta_params['HORIZ_POS_FULL']
    verti_pos_full = meta_params['VERTI_POS_FULL']
    #arts <- list of arteries
    #each artery is represented by ordered list of intersection labels
    colors = art_colormap(np.linspace(0.2,0.8,len(arts)))
    ctx.set_line_width(half_roadwidth*0.7)
    for a, art in enumerate(arts):
        for k in range(len(art)-1):
            ctx.move_to(horiz_pos_full[int(art[k][0])], verti_pos_full[int(art[k][-1])])
            ctx.line_to(horiz_pos_full[int(art[k+1][0])], verti_pos_full[int(art[k+1][-1])])
        r,g,b,alpha = colors[a]
        ctx.set_source_rgba(r, g, b, alpha)
        ctx.stroke()



