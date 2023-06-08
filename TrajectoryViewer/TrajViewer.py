#Trajectory Viewer V2
#gui imports
import tkinter as tk
from tkinter import filedialog as fd
import threading
from PIL import Image, ImageDraw, ImageTk

#other imports
import matplotlib.pyplot as plt
import math
import numpy as np
import csv
import time

#Global variables
Ball_Ts = []
Ball_X = []
Ball_Y = []
Ypred_forward = []
Ypred_midfields = []
Ypred_defenders = []
Ypred_goalkeeper = []
Ball_Vx = []
Ball_Vy = []

# === you can change the for loop to fill y_pred_... with your custom prediction method ===
#You can use the variables above as input for the prediction
#This example uses the mean of the last 30 speeds to compute a slope

use_custom_pred = True #change this to false to keep what was already in Ypred
def prediction_custom():
    global Ypred_forward
    global Ypred_midfields
    global Ypred_defenders
    global Ypred_goalkeeper
    for i in range(30,len(Ball_Ts)):
        if sum(Ball_Vx[i-30:i]) != 0:
            a = sum(Ball_Vy[i-30:i])/sum(Ball_Vx[i-30:i])
            b = Ball_Y[i] - Ball_X[i]*a
            Ypred_goalkeeper[i] = -525*a + b
            Ypred_defenders[i] = -375*a + b
            Ypred_midfields[i] = -75*a + b
            Ypred_forward[i] = 225*a + b
        else:
            Ypred_goalkeeper[i] = 0
            Ypred_defenders[i] = 0
            Ypred_midfields[i] = 0
            Ypred_forward[i] = 0

#Canvas size
w = 1080
h = int(w*3.0/4.0)

#flags and misc
flag_render_traj = False
flag_render_select = False

canvas_traj = [] #handles for the selected traj lines
canvas_pts = [] #handles for the points
canvas_background = None #image of the whole plot

#Misc functions
def mm2pix(coord):
    return [int(coord[0]*w/1220 + w/2), int(-coord[1]*h/915 + h/2)]

def image_plot(x, y, subsampling=1, color="black"):
    global canvas_background
    image = Image.new("RGB", (w, h), (255,255,255))
    draw = ImageDraw.Draw(image)
    subsampling = max(subsampling, 1)
    for i in range(0,min(len(x),len(y))-subsampling, subsampling):
        pointa = mm2pix([x[i], y[i]])
        pointb = mm2pix([x[i+subsampling], y[i+subsampling]])
        draw.line([pointa[0], pointa[1], pointb[0], pointb[1]], (200,200,200))
    #draw the borders
    p1 = mm2pix([430,305])
    p2 = mm2pix([600,106])
    draw.line([p1[0], p1[1], p2[0], p2[1]], (0,0,0), width=2)
    p1 = mm2pix([600,-106])
    draw.line([p2[0], p2[1], p1[0], p1[1]], (0,0,0), width=2)

    p2 = mm2pix([430,-305])
    draw.line([p1[0], p1[1], p2[0], p2[1]], (0,0,0), width=2)
    p1 = mm2pix([-430,-305])
    draw.line([p2[0], p2[1], p1[0], p1[1]], (0,0,0), width=2)

    p2 = mm2pix([-600,-106])
    draw.line([p1[0], p1[1], p2[0], p2[1]], (0,0,0), width=2)
    p1 = mm2pix([-600,106])
    draw.line([p2[0], p2[1], p1[0], p1[1]], (0,0,0), width=2)

    p2 = mm2pix([-430,305])
    draw.line([p1[0], p1[1], p2[0], p2[1]], (0,0,0), width=2)
    p1 = mm2pix([430,305])
    draw.line([p2[0], p2[1], p1[0], p1[1]], (0,0,0), width=2)

    canvas_background = ImageTk.PhotoImage(image=image)
    canvas.create_image(0,0,image=canvas_background ,anchor='nw')

#gui functions
def btn_file_handle(): #to open a file
    global Ball_Ts
    global Ball_X
    global Ball_Y
    global Ypred_forward
    global Ypred_midfields
    global Ypred_defenders
    global Ypred_goalkeeper
    global Ball_Vx
    global Ball_Vy

    global flag_render_traj
    global flag_render_select

    Ball_Ts = []
    Ball_X = []
    Ball_Y = []
    Ypred_forward = []
    Ypred_midfields = []
    Ypred_defenders = []
    Ypred_goalkeeper = []
    Ball_Vx = []
    Ball_Vy = []
    name= fd.askopenfilename()
    lbl_filename.config(text=name)
    file = open(name, "r", encoding="utf8")
    tsv_reader = csv.reader(file, delimiter="\t")
    flag_start = False
    counter = 0
    for row in tsv_reader:
        if round(float(row[0])) == 0: #detect end of data (if Ts is 0)
            break
        if flag_start:
            Ball_Ts.append(float(row[0]))
            Ball_X.append(float(row[1]))
            Ball_Y.append(float(row[2]))
            Ypred_forward.append(float(row[3]))
            Ypred_midfields.append(float(row[4]))
            Ypred_defenders.append(float(row[5]))
            Ypred_goalkeeper.append(float(row[6]))
            Ball_Vx.append(float(row[7]))
            Ball_Vy.append(float(row[8]))
            counter += 1
        flag_start = True
    print(counter)
    if use_custom_pred:
        prediction_custom()
    scale_start.config(to=len(Ball_Ts)-1)
    scale_select.config(to=len(Ball_Ts)-1)
    scale_select.set(0)
    scale_end.config(to=len(Ball_Ts)-1)
    scale_end.set(len(Ball_Ts)-1)
    image_plot(Ball_X, Ball_Y)
    flag_render_traj = True
    flag_render_select = True

def scale_handle(event):
    if scale_start.get() >= scale_end.get():
        scale_start.set(scale_end.get()-1)
    scale_select.config( from_=scale_start.get(), to=scale_end.get())
    global flag_render_traj
    global flag_render_select
    flag_render_traj = True
    flag_render_select = True

def scale_select_handle(event):
    global flag_render_select
    flag_render_select = True

def render_pts_handle():
    global flag_render_select
    flag_render_select = True

#canvas drawing functions
def canvas_plot(canvas, x, y, subsampling=1, color="black"):
    handles = []
    subsampling = max(subsampling, 1)
    for i in range(0,min(len(x),len(y))-subsampling, subsampling):
        pointa = mm2pix([x[i], y[i]])
        pointb = mm2pix([x[i+subsampling], y[i+subsampling]])
        handles.append(canvas.create_line(pointa[0], pointa[1], pointb[0], pointb[1], fill=color))
    return handles

def canvas_scatter(canvas, x, y, size = 4,color="black"):
    [x,y] = mm2pix([x,y])
    return canvas.create_oval(int(x+size/2), int(y+size/2), int(x-size/2), int(y-size/2), fill=color, outline=color)

def canvas_arrow(canvas, x0, y0, x1, y1, color="black"):
    [x0,y0] = mm2pix([x0,y0])
    [x1,y1] = mm2pix([x1,y1])
    return canvas.create_line(x0,y0,x1,y1, fill=color,arrow=tk.LAST)

def canvas_clear(canvas, handles):
    for i in handles:
        canvas.delete(i)
    handles.clear()

def update():
    global flag_render_traj
    global flag_render_select
    global canvas_pts
    global canvas_traj

    if len(Ball_Ts) != 0:
        start = scale_start.get()
        end = scale_end.get()
        select = scale_select.get()

        subsampling = math.ceil(abs(end-start)/1300.0) #poor performance if we try to plot more than 1000 lines
        #render the selected trajectory
        if flag_render_traj:
            canvas_clear(canvas, canvas_traj)
            canvas_traj = canvas_plot(canvas, Ball_X[start:end], Ball_Y[start:end], subsampling=subsampling, color="blue")
            flag_render_traj = False

        #render the points
        if flag_render_traj or flag_render_select:
            canvas_clear(canvas, canvas_pts)
            #plot ball
            canvas_pts.append(canvas_scatter(canvas, Ball_X[select], Ball_Y[select], size=6,color="orange"))
            canvas_pts.append(canvas_arrow(canvas, Ball_X[select], Ball_Y[select], Ball_X[select]+Ball_Vx[select]/10, Ball_Y[select]+Ball_Vy[select]/10))
            if plot_players.get():
                #forward
                color = "#B4E61E"
                if Ypred_forward[select] != 0:
                    color = "#1EE65A"
                canvas_pts.append(canvas_scatter(canvas, 225, Ypred_forward[select] + 208, color=color))
                canvas_pts.append(canvas_scatter(canvas, 225, Ypred_forward[select], color=color))
                canvas_pts.append(canvas_scatter(canvas, 225, Ypred_forward[select] - 208, color=color))

                #midfield
                color = "#B4E61E"
                if Ypred_midfields[select] != 0:
                    color = "#1EE65A"
                canvas_pts.append(canvas_scatter(canvas, -75, Ypred_midfields[select] + 240, color=color))
                canvas_pts.append(canvas_scatter(canvas, -75, Ypred_midfields[select] + 120, color=color))
                canvas_pts.append(canvas_scatter(canvas, -75, Ypred_midfields[select], color=color))
                canvas_pts.append(canvas_scatter(canvas, -75, Ypred_midfields[select] - 120, color=color))
                canvas_pts.append(canvas_scatter(canvas, -75, Ypred_midfields[select] - 240, color=color))

                #defenders
                color = "#B4E61E"
                if Ypred_defenders[select] != 0:
                    color = "#1EE65A"
                canvas_pts.append(canvas_scatter(canvas, -375, Ypred_defenders[select] + 120, color=color))
                canvas_pts.append(canvas_scatter(canvas, -375, Ypred_defenders[select] - 120, color=color))
                
                #goalkeeper
                color = "#B4E61E"
                if Ypred_goalkeeper[select] != 0:
                    color = "#1EE65A"
                canvas_pts.append(canvas_scatter(canvas, -525, Ypred_goalkeeper[select], color=color))

            if plot_rodcenter.get():
                color = "#F080F0"
                canvas_pts.append(canvas_scatter(canvas, 225, Ypred_forward[select], color=color))
                canvas_pts.append(canvas_scatter(canvas, -75, Ypred_midfields[select], color=color))
                canvas_pts.append(canvas_scatter(canvas, -375, Ypred_defenders[select], color=color))
                canvas_pts.append(canvas_scatter(canvas, -525, Ypred_goalkeeper[select], color=color))
            
            #update the label
            text = "----------------------------------------\n"
            text += "Subsampling: {0}\n".format(subsampling)
            text += "T          : {0}s / {1} samples\n".format(round(Ball_Ts[select],2),select)
            text += u"\u0394T         : {0}s / {1} samples\n\n".format(round(Ball_Ts[end]-Ball_Ts[start],3),end-start)
            text += "Ball pos   : {0}, {1}\n".format(round(Ball_X[select],2), round(Ball_Y[select],2))
            text += "Ball speed : {0}, {1}\n".format(round(Ball_Vx[select],2), round(Ball_Vy[select],2))
            text += "Peak speed : {0}\n\n".format(round(max([(Ball_Vx[i]**2 + Ball_Vy[i]**2)**0.5 for i in range(start, end+1)])))
            
            #time to next y_pred
            t_forward = None
            e_forward = None
            t_mid = None
            e_mid = None
            t_def = None
            e_def = None
            t_goal = None
            e_goal = None
            for i in range(select, end-1):
                if (Ball_X[i]-225)*(Ball_X[i+1]-225) <= 0 and t_forward==None: #if sign of distance is not same between x and x+1
                    t_forward = round(Ball_Ts[i]-Ball_Ts[select],3)
                    weighta = 1/abs(Ball_X[i]-225)
                    weightb = 1/abs(Ball_X[i+1]-225)
                    e_forward = round(abs((Ypred_forward[select]-Ball_Y[i])*weighta + (Ypred_forward[select]-Ball_Y[i+1])*weightb)/(weighta + weightb),2)

                elif (Ball_X[i]+75)*(Ball_X[i+1]+75) <= 0 and t_mid==None:
                    t_mid = round(Ball_Ts[i]-Ball_Ts[select],3)
                    weighta = 1/abs(Ball_X[i]+75)
                    weightb = 1/abs(Ball_X[i+1]+75)
                    e_mid = round(abs((Ypred_midfields[select]-Ball_Y[i])*weighta + (Ypred_midfields[select]-Ball_Y[i+1])*weightb)/(weighta + weightb),2)

                elif (Ball_X[i]+375)*(Ball_X[i+1]+375) <= 0 and t_def==None:
                    t_def = round(Ball_Ts[i]-Ball_Ts[select],3)
                    weighta = 1/abs(Ball_X[i]+375)
                    weightb = 1/abs(Ball_X[i+1]+375)
                    e_def = round(abs((Ypred_defenders[select]-Ball_Y[i])*weighta + (Ypred_defenders[select]-Ball_Y[i+1])*weightb)/(weighta + weightb),2)

                elif (Ball_X[i]+525)*(Ball_X[i+1]+525) <= 0 and t_goal==None:
                    t_goal = round(Ball_Ts[i]-Ball_Ts[select],3)
                    weighta = 1/abs(Ball_X[i]+525)
                    weightb = 1/abs(Ball_X[i+1]+525)
                    e_goal = round(abs((Ypred_goalkeeper[select]-Ball_Y[i])*weighta + (Ypred_goalkeeper[select]-Ball_Y[i+1])*weightb)/(weighta + weightb),2)

            text += u"\u0394T forward : {0}s\n".format(t_forward)
            text += u"\u0394X forward : {0}mm\n\n".format(e_forward)

            text += u"\u0394T mid     : {0}s\n".format(t_mid)
            text += u"\u0394X mid     : {0}mm\n\n".format(e_mid)

            text += u"\u0394T defender: {0}s\n".format(t_def)
            text += u"\u0394X defender: {0}mm\n\n".format(e_def)

            text += u"\u0394T goal    : {0}s\n".format(t_goal)
            text += u"\u0394X goal    : {0}mm\n\n".format(e_goal)

            lbl_data.config(text=text)

            flag_render_select = False

    root.after(30, update) #call every 30ms


#GUI definition
root = tk.Tk()
root.title("Trajectory Viewer by Severin Konishi")
frame_left = tk.Frame(root)
frame_right = tk.Frame(root)
frame_bottom = tk.Frame(root)

frame_left.grid(row=0,column=0)
frame_right.grid(row=0,column=1)
frame_bottom.grid(row=1,column=0, columnspan=2)

#right frame
canvas = tk.Canvas(frame_right, width=w, height=h)
canvas.pack()

#left frame
lbl_filename = tk.Label(frame_left, text="filename")
lbl_filename.grid(row=0, column=0)

button_file = tk.Button(frame_left, text="open file", command=btn_file_handle)
button_file.grid(row=1, column=0)

plot_players = tk.IntVar()
check_players = tk.Checkbutton(frame_left, text='Plot Players', variable=plot_players, command=render_pts_handle)
check_players.grid(row=2, column=0, sticky="W")

plot_rodcenter = tk.IntVar()
check_rodcenter = tk.Checkbutton(frame_left, text='Plot Rod center', variable=plot_rodcenter, command=render_pts_handle)
check_rodcenter.grid(row=3, column=0, sticky="W")

lbl_data = tk.Label(frame_left, text="data:", anchor="w", justify=tk.LEFT, font=('Courier', 10))
lbl_data.grid(row=4, column=0, sticky="W")

#bottom frame
scale_start = tk.Scale(frame_bottom, orient=tk.HORIZONTAL, command=scale_handle, length=w)
scale_select = tk.Scale(frame_bottom, orient=tk.HORIZONTAL, command=scale_select_handle, length=w)
scale_end = tk.Scale(frame_bottom, orient=tk.HORIZONTAL, command=scale_handle, length=w)
scale_end.set(100)

scale_start.pack()
scale_select.pack()
scale_end.pack()

update()
root.mainloop()
