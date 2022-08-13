import numpy as np
import math
import cairo
import pandas as pd

WIDTH, HEIGHT = 600, 600

#Num. roads
NUM_HORIZ = 4
NUM_VERTI = 4

#Dimensioning
MARGIN_TO_CENTRE = 0.2
MARGIN_TO_PLOTEDGE = 0.05
HALF_ROADWIDTH = 0.025

#Colours
BG_R, BG_G, BG_B = 240/255, 240/255, 240/255
LN_R, LN_G, LN_B = 40/255 , 40/255 , 40/255

INT_R, INT_G, INT_B, INT_ALPHA = 109/255, 82/255, 66/255, 0.25
OUT_R, OUT_G, OUT_B, OUT_ALPHA  = 87/255, 137/255, 87/255, 0.25

horiz_pos = list(np.linspace(MARGIN_TO_CENTRE, 1-MARGIN_TO_CENTRE,NUM_HORIZ))
verti_pos = list(np.linspace(MARGIN_TO_CENTRE, 1-MARGIN_TO_CENTRE,NUM_VERTI))

horiz_pos_full = [MARGIN_TO_PLOTEDGE] + horiz_pos + [1-MARGIN_TO_PLOTEDGE]
verti_pos_full = [MARGIN_TO_PLOTEDGE] + verti_pos + [1-MARGIN_TO_PLOTEDGE]

def edge_pos(A,B):
    Ai, Aj = int(A[0]), int(A[-1])
    Bi, Bj = int(B[0]), int(B[-1])
    edge_v = (verti_pos_full[Aj] + verti_pos_full[Bj])/2
    edge_h = (horiz_pos_full[Ai] + horiz_pos_full[Bi])/2
    return edge_h, edge_v

with cairo.SVGSurface("example.svg", WIDTH, HEIGHT) as surface:
    ctx = cairo.Context(surface)

    ctx.scale(WIDTH, HEIGHT)  # Normalizing the canvas
    pat = cairo.SolidPattern(BG_R, BG_G, BG_B)
    conflict = cairo.SolidPattern(INT_R, INT_G, INT_B, INT_ALPHA)
    input = cairo.SolidPattern(OUT_R, OUT_G, OUT_B, OUT_ALPHA)
    ctx.rectangle(0, 0, 1, 1)  # Rectangle(x0, y0, x1, y1)
    ctx.set_source(pat)
    ctx.fill()

    #%% Roads
    #Creating road outlines
    for h in horiz_pos:
        ctx.move_to(h-HALF_ROADWIDTH, MARGIN_TO_PLOTEDGE)
        ctx.line_to(h-HALF_ROADWIDTH, 1-MARGIN_TO_PLOTEDGE)
        ctx.move_to(h+HALF_ROADWIDTH, MARGIN_TO_PLOTEDGE)
        ctx.line_to(h+HALF_ROADWIDTH, 1-MARGIN_TO_PLOTEDGE) 
    for v in verti_pos:
        ctx.move_to(MARGIN_TO_PLOTEDGE, v-HALF_ROADWIDTH)
        ctx.line_to(1-MARGIN_TO_PLOTEDGE, v-HALF_ROADWIDTH)
        ctx.move_to(MARGIN_TO_PLOTEDGE, v+HALF_ROADWIDTH)
        ctx.line_to(1-MARGIN_TO_PLOTEDGE, v+HALF_ROADWIDTH) 
    ctx.set_source_rgb(LN_R, LN_G, LN_B)  # Solid color
    ctx.set_line_width(0.003)
    ctx.stroke()
    
    #%% Intersections
    #Clearing the outlines of conflict areas
    for h in horiz_pos:
        ctx.move_to(h, MARGIN_TO_PLOTEDGE)
        ctx.line_to(h, 1-MARGIN_TO_PLOTEDGE)
    for v in verti_pos:
        ctx.move_to(MARGIN_TO_PLOTEDGE, v)
        ctx.line_to(1-MARGIN_TO_PLOTEDGE, v)
    ctx.set_source_rgb(BG_R, BG_G, BG_B)  # Solid color
    ctx.set_line_width(0.047)
    ctx.stroke()

    #Shading the conflict areas
    for i,h in enumerate(horiz_pos,start = 1):
        for j,v in enumerate(verti_pos,start = 1):
            ctx.rectangle(h-HALF_ROADWIDTH, v-HALF_ROADWIDTH, MARGIN_TO_PLOTEDGE, MARGIN_TO_PLOTEDGE)
    ctx.set_source(conflict)
    ctx.fill()

    #Labelling each itersection
    ctx.set_source_rgb(BG_R, BG_G, BG_B)
    ctx.select_font_face("Bahnschrift", cairo.FONT_SLANT_NORMAL, 
        cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(HALF_ROADWIDTH*0.8)

    for i,h in enumerate(horiz_pos,start = 1):
        for j,v in enumerate(verti_pos,start = 1):
            (x, y, width, height, dx, dy) = ctx.text_extents("%d,%d"%(i,j))
            # ctx.move_to(h-width/1.8, v+height/3)
            ctx.move_to(h-width, v+height)
            ctx.show_text("%d,%d"%(i,j))
            
    #%% Outer nodes
    #Shading each outer nodes
    for i,h in enumerate(horiz_pos,start = 1):
        ctx.move_to(h, MARGIN_TO_PLOTEDGE)
        ctx.arc(h, MARGIN_TO_PLOTEDGE, HALF_ROADWIDTH, 0, 2*math.pi)
    
        ctx.move_to(h, 1-MARGIN_TO_PLOTEDGE)
        ctx.arc(h, 1-MARGIN_TO_PLOTEDGE, HALF_ROADWIDTH, 0, 2*math.pi)
    
    for j,v in enumerate(verti_pos,start = 1):
        ctx.move_to(MARGIN_TO_PLOTEDGE, j)
        ctx.arc(MARGIN_TO_PLOTEDGE, v, HALF_ROADWIDTH, 0, 2*math.pi)
    
        ctx.move_to(1-MARGIN_TO_PLOTEDGE, j)
        ctx.arc(1-MARGIN_TO_PLOTEDGE, v, HALF_ROADWIDTH, 0, 2*math.pi)
        
    ctx.set_source(input)
    ctx.fill()
    
    #Labelling each outer nodes
    ctx.set_source_rgb(BG_R, BG_G, BG_B)
    ctx.select_font_face("Bahnschrift", cairo.FONT_SLANT_NORMAL, 
        cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(HALF_ROADWIDTH*0.8)
    for i,h in enumerate(horiz_pos,start = 1):
        (x, y, width, height, dx, dy) = ctx.text_extents("%d,%d"%(i,0))
        ctx.move_to(h-width*0.9, MARGIN_TO_PLOTEDGE*1.4)
        # ctx.move_to(h-width/2, MARGIN_TO_PLOTEDGE+0.01)
        ctx.show_text("%d,%d"%(i,0))
        
        (x, y, width, height, dx, dy) = ctx.text_extents("%d,%d"%(i,NUM_VERTI+1))
        ctx.move_to(h-width*0.9, 1-MARGIN_TO_PLOTEDGE/1.6)
        # ctx.move_to(h-width/2, 1-MARGIN_TO_PLOTEDGE+0.01)
        ctx.show_text("%d,%d"%(i,NUM_VERTI+1))
    
    for j,v in enumerate(verti_pos,start = 1):
        (x, y, width, height, dx, dy) = ctx.text_extents("%d,%d"%(0,j))
        ctx.move_to(MARGIN_TO_PLOTEDGE/1.6, v+height)
        # ctx.move_to(MARGIN_TO_PLOTEDGE-0.016, v+height/3)
        ctx.show_text("%d,%d"%(0,j))
        
        (x, y, width, height, dx, dy) = ctx.text_extents("%d,%d"%(NUM_HORIZ+1,j))
        ctx.move_to(1-MARGIN_TO_PLOTEDGE*1.4, v+height)
        # ctx.move_to(1-MARGIN_TO_PLOTEDGE-0.016, v+height/3)
        ctx.show_text("%d,%d"%(NUM_HORIZ+1,j))
        
    #Edge labelling
    ctx.set_source_rgb(LN_R, LN_G, LN_B)
    ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, 
        cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(HALF_ROADWIDTH)

    weights = pd.read_excel("data0508.xlsx",sheet_name="exp",index_col=0)
    adj = np.where(np.triu(weights.to_numpy())>0)
    
    for m,n in zip(adj[0],adj[1]):
        edge_h, edge_v = edge_pos(weights.index[m], weights.columns[n])
        (x, y, width, height, dx, dy) = ctx.text_extents("%.2f" %weights.iloc[m,n])
        ctx.move_to(edge_h-dx/2, edge_v+height/2)
        ctx.show_text("%.2f" %weights.iloc[m,n])
    # surface.write_to_png("example.png")