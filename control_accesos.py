import face_recognition
import cv2
import numpy as np
import os, os.path
import tkinter as tk
from tkinter import ttk
import datetime
from sqlalchemy import create_engine, text, MetaData, Table, select, and_
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =  'mysql://luis:Luis+2@localhost/Face2Face'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)




class Colaboradores(db.Model):
    __tablename__='Colaboradores'
    id = db.Column('ID_C',db.Integer,primary_key=True)
    Nombre = db.Column('Nombre',db.Unicode)
    Apellido = db.Column('Apellido',db.Unicode)
    Telefono = db.Column('Teléfono',db.Integer)
    Email = db.Column('Email',db.Unicode)
    Tipo = db.Column('Tipo',db.Unicode)

def Escribir_Col(id_,Nombre_,Apellido_,Telefono_,Email_,Tipo_):
    Col = Colaboradores(id=id_,Nombre=Nombre_,Apellido=Apellido_,Telefono=Telefono_,Email=Email_,Tipo=Tipo_)
    db.session.add(Col)
    db.session.commit()

def Delete_Col(id_):
    user= Colaboradores.query.get(id_)
    db.session.delete(user)
    db.session.commit()

def print_col():
    example = Colaboradores.query.all()
    print('{:3} | {:10}| {:10} | {:10} | {:20} | {:10}'.format("ID","Nombre","Apellido","Telefono","Email","Tipo"))
    for ex in example:
        print('{:3}  {:10.10} | {:10.10}   {:10.10}   {:20.20}   {:10}'.format(ex.id,ex.Nombre,ex.Apellido,str(ex.Telefono),ex.Email,ex.Tipo))
    


#SQL function
def SQL_var(first_name, last_name, tel, buss):
    global number_files

    now = datetime.datetime.now()
    date_time = str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)
    date_day = str(now.day) + "/" + str(now.month) + "/" + str(now.year)

    idr = 1 #ID de Registro(Incremental)
    fecha = date_time
    hora = date_day
    idc = number_files #ID de Colaborador(Único para cada empleado)
    nombre = first_name
    apellido = last_name
    tel = str(tel) #Extension
    email = first_name + '@hotmail.com'
    tipo = buss #Colaborador, Auditor, Consultor, Cliente, Provedor
    Escribir_Col(idc,nombre,apellido,tel,email,tipo)
   

Photos folder path
string_photos = "/home/luis/Desktop/control_acceso/photos/"
string_reg = "/home/luis/Desktop/control_acceso/day_registration/"
DEASM = "/home/luis/Desktop/control_acceso/DEASM/DEASM.mp4"




#System variables
break_var = 1
ss_var = 1
del_var = 1
entrada_var = 0
row_var = 3
button_var = 0

def only_numerics(num):
    seq_type= type(num)
    return seq_type().join(filter(seq_type.isdigit, num))

#Buttons functions
def registration_function():
    if button_var == 0:
        if FN_reg.get() == "":
            print("Please enter the first name")
        elif LN_reg.get() == "":
            print("Please enter the last name")
        elif Cellphone_reg.get() == "":
            print("Please enter the cellphone")
        elif Cellphone_reg.get() < "0000000000" or Cellphone_reg.get() > "9999999999" or len(Cellphone_reg.get()) != 10:
            print("Please enter a valid cellphone")
        elif Bus.get() == "":
            print("Please enter the bussiness")
        else:
            print("First Name: %s\nLast Name: %s\nCellphone: %s\nBussiness: %s" % ( FN_reg.get(), LN_reg.get(), Cellphone_reg.get() , Bus.get()) )
            global ss_var
            ss_var = 0
            SQL_var(FN_reg.get(), LN_reg.get(), Cellphone_reg.get(), Bus.get())

def delete_function():
    if button_var == 0:
        global number_files
        if FN_del.get() == "":
            print("Please enter the first name")
        elif LN_del.get() == "":
            print("Please enter the last name")
        else:
            global number_files, known_face_names
            for i in range(number_files):
                if known_face_names[i] == FN_del.get() + LN_del.get():
                    global ss_var
                    global del_var
                    del_var = 0
                    ss_var = 0
                    # t = text("delete from Colaboradores where ID_C =" + str(number_files-1))
                    # resultwrite = connection.execute(t)
                    Delete_Col(number_files-1)
                    break

def exit_program():
    global break_var
    break_var = 0

def entries(func_name, index, func_reg_name):
    global entrada_var, row_var, day_registration, Re
    Re = tk.PhotoImage(file=func_reg_name)
    entrada_var += 1
    now = datetime.datetime.now()
    date_time = str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)
    date_day = str(now.day) + "/" + str(now.month) + "/" + str(now.year)
    date = str(func_name) + " enter at " + date_time + " in " + date_day
    tk.Label(master.newWindow, text=date,font =('Arial Black', 12, 'bold'),bg='white').grid(row=row_var)
    tk.Label(master.newWindow, text='Registration photo:',font =('Arial Black', 12, 'bold'),bg='white').grid(row=0,column=1)
    tk.Label(master.newWindow, image=Re,bg='white').grid(row=1,column=1)
    row_var += 1
    day_registration[index] = 1

def change_button():
    global button_var
    if button_var == 0:
        tk.Button(master, image = OFF, command=change_button, bg='white').grid(row=1, column=1)
        tk.Button(master.newWindow, image = ON, command=change_button, bg='white').grid(row=0)
        button_var = 1
    else:
        tk.Button(master, image = ON, command=change_button, bg='white').grid(row=1, column=1)
        tk.Button(master.newWindow, image = OFF, command=change_button, bg='white').grid(row=0)
        button_var = 0

#Images function
def img_func():

    global number_files, array_image, known_face_encodings, known_face_names, day_registration, x

    #Count the number of images to cretae the arrays
    list = os.listdir(string_photos)
    number_files = len(list)

    # Create arrays of known face encodings and their names
    array_image = [0] * number_files
    known_face_encodings = [0] * number_files
    known_face_names = [0] * number_files
    day_registration = [0] * number_files
    x = number_files - 1

    # Load the pictures, learn how to recognize it and put them names
    for i in range(number_files):
        array_image[i] = face_recognition.load_image_file(string_photos + str(list[x]))
        known_face_encodings[i] = face_recognition.face_encodings(array_image[i])[0]
        day_registration[i] = 0
        index = list[x].find(".")
        known_face_names[i] = str(list[x][:index])
        x = x - 1

#GUI Code
master = tk.Tk()
master.title("Register center")
master.configure(bg='white')

FN_reg = tk.Entry(master)
FN_del = tk.Entry(master)
LN_reg = tk.Entry(master)
LN_del = tk.Entry(master)
Cellphone_reg = tk.Entry(master)





SS = tk.PhotoImage(file="./GUI_photos/SS.png")
Ex = tk.PhotoImage(file="./GUI_photos/exit.png")
F2F = tk.PhotoImage(file="./GUI_photos/f2f.png")
Trash = tk.PhotoImage(file="./GUI_photos/trash.png")
ON = tk.PhotoImage(file="./GUI_photos/On.png")
OFF = tk.PhotoImage(file="./GUI_photos/Off.png")
REG = tk.PhotoImage(file="./GUI_photos/rec.png")


tk.Label(master, image = F2F, bg='white').grid(row=0,column=1)
tk.Button(master, image = ON, command=change_button, bg='white').grid(row=1, column=1)

tk.Label(master, text="REGISTRATION",font =('Arial Black', 17, 'bold'),bg='white').grid(row=2)
tk.Label(master, text="DELETE PERSON",font =('Arial Black', 17, 'bold'),bg='white').grid(row=2,column=2)

tk.Label(master, text="First Name",font =('Arial Black', 15),bg='white').grid(row=3)
FN_reg.grid(row=4)
tk.Label(master, text="First Name",font =('Arial Black', 15),bg='white').grid(row=3,column=2)
FN_del.grid(row=4,column=2)

tk.Label(master, text="Last Name",font =('Arial Black', 15),bg='white').grid(row=5)
LN_reg.grid(row=6)
tk.Label(master, text="Last Name",font =('Arial Black', 15),bg='white').grid(row=5,column=2)
LN_del.grid(row=6,column=2)

tk.Label(master, text="Cellphone",font =('Arial Black', 15),bg='white').grid(row=7)
Cellphone_reg.grid(row=8)

tk.Label(master, text="Business",font =('Arial Black', 15),bg='white').grid(row=9)
Bus = tk.StringVar()
ComboBox = ttk.Combobox(master, textvariable = Bus,  values=["Colaborador", "Cliente", "Proveedor", "Auditor"]).grid(row=10)

tk.Label(master, bg='white').grid(row=11)

tk.Button(master, image = SS, command=registration_function, bg='white').grid(row=12)
tk.Button(master, image = Ex, command=exit_program, bg='white').grid(row=12,column=1)
tk.Button(master, image = Trash, command=delete_function, bg='white').grid(row=12,column=2)
tk.Button(master, image = REG, command=print_col, bg='white').grid(row=14,column=2)
tk.Label(master, text="Beta version", bg='white', fg='gray', font =('Batang', 10)).grid(row=13,column=1)

master.newWindow = tk.Toplevel(master.master)
master.newWindow.title("Entries")
master.newWindow.configure(bg='white')

tk.Button(master.newWindow, image = OFF, command=change_button, bg='white').grid(row=0)
tk.Label(master.newWindow, text='Day registration:', font =('Arial Black', 15, 'bold'), bg='white').grid(row=1)

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

#Call first image function
img_func()

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
scale_percent = 15 # percent of original size
tolerance_var = 0.5

ret, frame = video_capture.read()
width = int(frame.shape[1] * scale_percent / 100)
height = int(frame.shape[0] * scale_percent / 100)
dim = (width, height)

if not ret:
    print("Can't receive frame. Exiting ...")
    break_var == 0

while break_var == 1:
    
    #Update GUI
    master.update_idletasks()
    master.update()

    # Grab a single frame of video
    ret, frame = video_capture.read()
    if frame.shape[1] != 640:
        frame = cv2.resize(frame, (int(frame.shape[1]*0.85),int(frame.shape[0]*0.85)), interpolation = cv2.INTER_CUBIC)

    #Updating data after adding or erasing person
    if ss_var == 0:
        os.chdir(string_photos)
        if del_var == 1:
            cv2.imwrite(string_photos + FN_reg.get() + LN_reg.get() + ".jpg", frame)
        else:
            os.remove(string_photos + FN_del.get() + LN_del.get() + ".jpg")
            del_var = 1
        img_func()
        ss_var = 1

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance_var)
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)

    process_this_frame = not process_this_frame
        
    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4
       
        #Daily entry registration
        if button_var == 1:
            for i in range(number_files):
                if day_registration[i] == 0 and name == known_face_names[i]:
                    reg_img = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
                    now = datetime.datetime.now()
                    date = "_" + str(now.day) + "_" + str(now.month) + "_" + str(now.year)
                    registration_name = string_reg + name + date + ".png"
                    cv2.imwrite(registration_name, reg_img)
                    entries(name, i, registration_name)

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)
    cv2.waitKey(1)

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()