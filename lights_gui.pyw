import json
import os
import tkinter

import phue
import rgbxy

with open(os.path.realpath("lights_gui.pyw").replace("lights_gui.pyw", "config.json")) as f:
    config = json.loads(f.read())

bridge = phue.Bridge(config["IP"])
bridge.connect()
ROOMS = [bridge.get_group()[group] for group in bridge.get_group()
         if bridge.get_group()[group]["type"] == "Room"]
DEVICES = bridge.get_light_objects("name")
converter = rgbxy.Converter()


def setup(room):
    master_frame = tkinter.Frame(root)
    master_frame.grid()
    for _ in ROOMS:
        if _["name"] == room:
            room = _
            break
    lights_column = 0
    plugs_column = 0
    tkinter.OptionMenu(master_frame, tkinter.StringVar(root, room["name"]), *[
                       room["name"] for room in ROOMS], command=lambda a, b=master_frame: destroy(a, b)).grid(row=0, column=0)
    frame = tkinter.LabelFrame(master=master_frame, text="Szene wählen")
    tkinter.OptionMenu(frame, tkinter.StringVar(), *[scene.name for scene in bridge.scenes if scene.type == "GroupScene" and list(
        map(str, scene.lights)) == sorted(room["lights"])], command=lambda a, b=room, c=master_frame: change_scene(a, b, c)).pack()
    frame.grid(row=1, column=0)
    for device in DEVICES:
        if str(DEVICES[device].light_id) in room["lights"]:
            if DEVICES[device].type == "Extended color light":
                x, y = DEVICES[device].xy
                bri = DEVICES[device].brightness
                red, green, blue = converter.xy_to_rgb(x, y, bri)
                frame = tkinter.LabelFrame(
                    master=master_frame, text=DEVICES[device].name)
                text = tkinter.StringVar(
                    root, {True: "Ausschalten", False: "Anschalten"}[DEVICES[device].on])
                tkinter.Button(master=frame, textvariable=text,
                               command=lambda a=text, b=device: toggle(a, b)).pack()
                tkinter.Scale(master=frame, label="Helligkeit", from_=0, to=255, variable=tkinter.IntVar(
                    root, DEVICES[device].brightness), orient=tkinter.HORIZONTAL, command=lambda value, a=device: change_brightness(value, a)).pack()
                tkinter.Scale(master=frame, label="Rot", from_=1, to=255, variable=tkinter.IntVar(
                    root, red), orient=tkinter.HORIZONTAL, command=lambda value, a=device: change_red(value, a)).pack()
                tkinter.Scale(master=frame, label="Grün", from_=1, to=255, variable=tkinter.IntVar(
                    root, green), orient=tkinter.HORIZONTAL, command=lambda value, a=device: change_green(value, a)).pack()
                tkinter.Scale(master=frame, label="Blau", from_=1, to=255, variable=tkinter.IntVar(
                    root, blue), orient=tkinter.HORIZONTAL, command=lambda value, a=device: change_blue(value, a)).pack()
                frame.grid(row=2, column=lights_column)
                lights_column += 1
            elif DEVICES[device].type == "On/Off plug-in unit":
                frame = tkinter.LabelFrame(
                    master=master_frame, text=DEVICES[device].name)
                text = tkinter.StringVar(
                    root, {True: "Ausschalten", False: "Anschalten"}[DEVICES[device].on])
                tkinter.Button(master=frame, textvariable=text,
                               command=lambda a=text, b=device: toggle(a, b)).pack()
                frame.grid(row=3, column=plugs_column)
                plugs_column += 1


def destroy(room, master_frame):
    master_frame.destroy()
    setup(room)


def toggle(text, device):
    DEVICES[device].on = not DEVICES[device].on
    text.set({True: "Ausschalten", False: "Anschalten"}[DEVICES[device].on])


def change_brightness(value, device):
    if DEVICES[device].on:
        DEVICES[device].brightness = int(value)


def change_red(value, device):
    if DEVICES[device].on:
        red = int(value)
        x, y = DEVICES[device].xy
        bri = DEVICES[device].brightness
        _, green, blue = converter.xy_to_rgb(x, y, bri)
        x, y = converter.rgb_to_xy(red, green, blue)
        DEVICES[device].xy = [x, y]


def change_green(value, device):
    if DEVICES[device].on:
        green = int(value)
        x, y = DEVICES[device].xy
        bri = DEVICES[device].brightness
        red, _, blue = converter.xy_to_rgb(x, y, bri)
        x, y = converter.rgb_to_xy(red, green, blue)
        DEVICES[device].xy = [x, y]


def change_blue(value, device):
    if DEVICES[device].on:
        blue = int(value)
        x, y = DEVICES[device].xy
        bri = DEVICES[device].brightness
        red, green, _ = converter.xy_to_rgb(x, y, bri)
        x, y = converter.rgb_to_xy(red, green, blue)
        DEVICES[device].xy = [x, y]


def change_scene(scene, room, master_frame):
    bridge.run_scene(room["name"], scene)
    destroy(room, master_frame)


root = tkinter.Tk()
root.title("Lights GUI")
root.resizable(False, False)
setup(ROOMS[0])
root.mainloop()
