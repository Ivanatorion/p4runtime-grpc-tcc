import Tkinter as tk
import os

from model.DB_mgmt import *

from model.objects.SwitchObject import *
from model.objects.SwitchTableObject import *
from model.objects.SwitchTableActionObject import *
from model.objects.SwitchRegisterObject import *
from model.objects.User import *

content_widgets = []

cv_content = None
cv_canvas = None
lb_content = None

def onFrameConfigure(canvas):
    print canvas.bbox("all")
    canvas.configure(scrollregion=canvas.bbox("all"))

def startWin():
    global cv_content
    global cv_canvas
    global lb_content

    root = tk.Tk()

    lb_buttons = tk.Listbox(root)
    lb_buttons.pack({"side": "left", "anchor" : "nw"})

    cv_content = tk.Canvas(root)
    cv_content.pack({"side" : "right", "expand" : True})

    cv_canvas = tk.Canvas(cv_content)

    lb_content = tk.Frame(cv_canvas)

    lb_content_scroll = tk.Scrollbar(cv_content, command=cv_canvas.yview)
    lb_content_scroll.pack(side="right", fill="y")

    cv_canvas.configure(yscrollcommand=lb_content_scroll.set)
    cv_canvas.pack(side="left", fill="both", expand=True)
    cv_canvas.create_window((0,0), window=lb_content, anchor="nw")

    lb_content.bind("<Configure>", lambda event, canvas=cv_canvas: onFrameConfigure(canvas))

    print lb_content.keys()

    bUsers = tk.Button(lb_buttons)
    bUsers["text"] = "Users"
    bUsers["width"] = 20
    bUsers["height"] = 2
    bUsers["command"] = but_users
    bUsers.pack({"side": "top"})

    bDevices = tk.Button(lb_buttons)
    bDevices["text"] = "Devices"
    bDevices["width"] = 20
    bDevices["height"] = 2
    bDevices["command"] = but_devices
    bDevices.pack({"side": "top"})

    bApps = tk.Button(lb_buttons)
    bApps["text"] = "Apps"
    bApps["width"] = 20
    bApps["height"] = 2
    bApps.pack({"side": "top"})

    bIFC = tk.Button(lb_buttons)
    bIFC["text"] = "vIFC"
    bIFC["width"] = 20
    bIFC["height"] = 2
    bIFC.pack({"side": "top"})

    return root

def but_users():
    global lb_content
    global content_widgets

    for widget in content_widgets:
        widget.pack_forget()
        widget.grid_forget()

    queryCursor.execute("SELECT * FROM users")
    users = queryCursor.fetchall()

    header = tk.Entry(lb_content, width = 25)
    header.grid(row=0, column=0)
    header.insert(tk.END, "ID")
    content_widgets.append(header)
    header = tk.Entry(lb_content, width = 25)
    header.grid(row=0, column=1)
    header.insert(tk.END, "Name")
    content_widgets.append(header)

    for i in range(0, 4):
        for user in range(0, len(users)):
            e = tk.Entry(lb_content, width = 25)
            e.grid(row = i * 4 + user + 1, column = 0)
            e.insert(tk.END, str(users[user][0]))
            content_widgets.append(e)
            e = tk.Entry(lb_content, width = 25)
            e.grid(row = i * 4 + user + 1, column = 1)
            e.insert(tk.END, str(users[user][1]))
            content_widgets.append(e)

def but_devices():
    global lb_content
    global content_widgets

    for widget in content_widgets:
        widget.pack_forget()
        widget.grid_forget()

if __name__ == "__main__":
    root = startWin()
    print root
    root.mainloop()
