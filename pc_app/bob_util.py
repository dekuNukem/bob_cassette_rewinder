import os
import time
from datetime import datetime
import webbrowser
import check_update
from functools import partial
from tkinter import *
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
import serial.tools.list_ports
import serial
import urllib.request

wash_count_lookup = {0x4e:30, 0x4d:29, 0x4c:28, 0x4b:27, 0x4a:26, 0x49:25, 0x48:24, 0x47:23, 0x46:22, 0x45:21, 0x44:20, 0x43:19, 0x42:18, 0x41:17, 0x40:16, 0x5f:15, 0x5e:14, 0x5d:13, 0x5c:12, 0x5b:11, 0x5a:10, 0x59:9, 0x58:8, 0x57:7, 0x56:6, 0x55:5, 0x54:4, 0x53:3, 0x52:2, 0x51:1, 0x50:0}

THIS_VERSION_NUMBER = '0.1.0'
MAIN_WINDOW_WIDTH = 600
MAIN_WINDOW_HEIGHT = 360
PADDING = 10
HEIGHT_CONNECT_LF = 50
discord_link_url = "https://raw.githubusercontent.com/dekuNukem/daytripper/master/resources/discord_link.txt"

def open_user_manual_url():
    webbrowser.open('https://github.com/dekuNukem/bob_cassette_rewinder/blob/master/user_manual.md')

def open_discord_link():
    try:
        webbrowser.open(str(urllib.request.urlopen(discord_link_url).read().decode('utf-8')).split('\n')[0])
    except Exception as e:
        messagebox.showerror("Error", "Failed to open discord link!\n"+str(e))

def create_help_window():
    help_window = Toplevel(root)
    help_window.title("Bob Rewinder utility help")
    help_window.geometry("280x130")
    help_window.resizable(width=FALSE, height=FALSE)

    user_manual_label = Label(master=help_window, text="Not sure what to do? Please read...")
    user_manual_label.place(x=35, y=5)
    user_manual_button = Button(help_window, text="User Manual", command=open_user_manual_url)
    user_manual_button.place(x=60, y=30, width=160)

    discord_label = Label(master=help_window, text="Questions or comments? Ask in...")
    discord_label.place(x=35, y=60)
    discord_button = Button(help_window, text="Official Discord Chatroom", command=open_discord_link)
    discord_button.place(x=50, y=85, width=180)

def ensure_dir(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

root = Tk()
root.title("Bob Rewinder Utility v" + THIS_VERSION_NUMBER)
root.geometry(str(MAIN_WINDOW_WIDTH) + "x" + str(MAIN_WINDOW_HEIGHT))
root.resizable(width=FALSE, height=FALSE)

# ------------- serial select -------------

connection_lf = LabelFrame(root, text="Connection", width=MAIN_WINDOW_WIDTH - PADDING*2, height=HEIGHT_CONNECT_LF)
connection_lf.place(x=PADDING, y=0)
root.update()

serial_var = StringVar()
serial_var.set(' ')
OptionList = ['']
serial_optlist = OptionMenu(connection_lf, serial_var, *OptionList)
serial_optlist.place(x=120, y=0, width=265)
ser = serial.Serial()
ser.baudrate = 115200
raw_content_label_stringvar = StringVar()
hwif_label_stringvar = StringVar()
bin_dict = {}
fw_ver_string = ''
byte_list = []

def serial_setname(wtf):
    serial_var.set(wtf)

def serial_dropdown_refresh():
    serial_optlist['menu'].delete(0, 'end')
    port_list = serial.tools.list_ports.comports()
    port_list.sort(key=lambda x: str(x.device))
    for item in port_list:
        port_name = str(item.device)
        serial_optlist['menu'].add_command(label=port_name, command=partial(serial_setname, port_name))
    if serial_var.get() == ' ' or serial_var.get() not in [str(x.device) for x in port_list]:
        serial_var.set(str(port_list[0].device))
    usb_port_list = [str(x.device) for x in port_list if 'usb' in str(x.device).lower()]
    if len(usb_port_list) > 0:
        serial_var.set(usb_port_list[0])

def make_raw_content_string():
    byte_str = ''
    for index, item in enumerate(byte_list):
        if index != 0 and index % 64 == 0:
            byte_str += '\n'
        if 32 <= item <= 126:
            byte_str += chr(item)
        else:
            byte_str += '.'
    return byte_str

def make_hw_info_string():
    cassette_str = make_raw_content_string()
    cassette_type = "Unknown"
    if "Classique" in cassette_str:
        cassette_type = "Pop"
    elif "Entretien" in cassette_str:
        cassette_type = "Rock'n'Roll"

    washes_left_str = "Unknown"
    washes_count_hex = bin_dict[0xa1]
    if washes_count_hex in wash_count_lookup:
        washes_left_str = str(wash_count_lookup[washes_count_hex])

    washes_left_str += " (" + str(hex(washes_count_hex)) + ")"
    
    return_str = "Type: " + cassette_type + "    Washes left: " + washes_left_str
    return return_str

def make_bob_dump_filename():
    cassette_str = make_raw_content_string()
    cassette_type = "Unknown"
    if "Classique" in cassette_str:
        cassette_type = "Pop"
    elif "Entretien" in cassette_str:
        cassette_type = "Rock"

    washes_count_hex = bin_dict[0xa1]
    if washes_count_hex in wash_count_lookup:
        washes_left_str = str(wash_count_lookup[washes_count_hex])

    return 'bobdump_' + current_time_str() + "_" + cassette_str[3:9] + '_' + cassette_type + "_" + str(washes_left_str) + "_washes_left"

def fw_update_click(what):
    webbrowser.open('https://github.com/dekuNukem/daytripper/blob/master/advanced_usage.md#usb-firmware-updates')

def serial_connect():
    global fw_ver_string
    global bin_dict
    global byte_list

    if len(serial_var.get()) <= 1:
        return

    bin_dict.clear()
    byte_list.clear()
    hwif_label_stringvar.set("")
    raw_content_label_stringvar.set("")

    ser.port = serial_var.get()
    ser.timeout = 0.75
    try:
        ser.open()
        ser.write("dump\n".encode('utf-8'))
        result = ser.readlines()
        ser.close()
    except Exception as e:
        messagebox.showerror("Error", 'Serial port exception:\n' + str(e))
        return
    result = [x.decode('utf-8') for x in result]
    for this_line in result:
        if "FW V" in this_line:
            fw_ver_string = this_line
        if 'done' in this_line:
            break
        if 'dump' in this_line:
            addr = int(this_line.split(' ')[1])
            data = int(this_line.split(' ')[2])
            bin_dict[addr] = data
        if 'no bob cassette detected' in this_line:
            messagebox.showerror("Error", "Bob Rewinder connected.\n\nHowever, no Bob Cassette detected!")
            return

    for i in range(len(bin_dict)):
        byte_list.append(bin_dict[i])

    if len(byte_list) != 256:
        messagebox.showerror("Error", 'Error reading Cassette:\n\nWrong EEPROM size!\n\nShould be 256B, got ' + str(len(byte_list)) + "B.")
        return

    hwif_label_stringvar.set(make_hw_info_string())
    raw_content_label_stringvar.set(make_raw_content_string())
    check_firmware_update()

user_guide_button = Button(connection_lf, text="How do I...", command=create_help_window)
user_guide_button.place(x=PADDING, y=0, width=100)
serial_refresh_button = Button(connection_lf, text="Refresh", command=serial_dropdown_refresh)
serial_refresh_button.place(x=395, y=0, width=80)
serial_connect_button = Button(connection_lf, text="Connect", command=serial_connect)
serial_connect_button.place(x=485, y=0, width=80)

hwif_lf = LabelFrame(root, text="Cassette Info", width=MAIN_WINDOW_WIDTH - PADDING*2, height=HEIGHT_CONNECT_LF)
hwif_lf.place(x=PADDING, y=60)
hwif_label = Label(master=hwif_lf, textvariable=hwif_label_stringvar, font='TkFixedFont')
hwif_label.place(x=PADDING, y=5)

raw_content_lf = LabelFrame(root, text="Raw Content", width=MAIN_WINDOW_WIDTH - PADDING*2, height=HEIGHT_CONNECT_LF*2)
raw_content_lf.place(x=PADDING, y=120)
raw_content_label = Label(master=raw_content_lf, textvariable=raw_content_label_stringvar, font='TkFixedFont')
raw_content_label.place(x=PADDING, y=5)

dump_lf = LabelFrame(root, text="Backup / Restore", width=MAIN_WINDOW_WIDTH - PADDING*2, height=HEIGHT_CONNECT_LF)
dump_lf.place(x=PADDING, y=230)

def current_time_str():
    ret = datetime.utcnow().isoformat(sep='T')
    return (ret[:19] + "Z").replace(':', '-')

def dump_to_file():
    serial_connect()
    if len(byte_list) != 256:
        return
    filename = filedialog.asksaveasfilename(initialfile=make_bob_dump_filename(), defaultextension='.bin')
    if len(filename) < 3:
        return
    try:
        with open(filename,'wb') as outfile:
            outfile.write(bytes(byte_list))
    except Exception as e:
        messagebox.showerror("Error", 'Save Failed:\n' + str(e))
        return
    messagebox.showinfo("Info", 'Success!')

def load_from_file():
    if len(serial_var.get()) <= 1:
        return

    yesno = messagebox.askyesno("Are you sure?", "This will overwrite the content on this cassette!\n\nMake sure you have a backup!\n\nProceed to restore?")
    if yesno is False:
        return

    filename = filedialog.askopenfilename()
    if len(filename) < 3:
        return
    bin_size = os.path.getsize(filename)
    if bin_size != 256:
        messagebox.showerror("Error", 'Wrong file size!\n\nShould be 256B, got ' + str(bin_size) + "B.")
        return
    restore_byte_array = b''
    try:
        with open(filename, 'rb') as myfile:
            restore_byte_array = myfile.read(256)
    except Exception as e:
        messagebox.showerror("Error", 'File open error:\n' + str(e))
    if len(restore_byte_array) != 256:
        messagebox.showerror("Error", 'Wrong file size!\n\nShould be 256B, got ' + str(len(restore_byte_array)) + "B.")
        return

    ser.port = serial_var.get()
    ser.timeout = 0.75

    try:
        ser.open()
        for index, item in enumerate(restore_byte_array):
            ser.write(("write " + str(index) + ' ' + str(item) + '\n').encode('utf-8'))
            result = ser.readline().decode('utf-8')
            if 'no bob cassette detected' in result:
                messagebox.showerror("Error", 'No bob cassette detected!')
                ser.close()
                return
            if int(result.split(' ')[1]) != index:
                messagebox.showerror("Error", 'Write out of sync! Maybe try again?')
                ser.close()
                return
        ser.close()
    except Exception as e:
        messagebox.showerror("Error", 'Serial port exception:\n' + str(e))
        ser.close()
        return

    messagebox.showinfo("Info", 'Success!')
    serial_connect()

dump_button = Button(dump_lf, text="Dump this cassette to file...", command=dump_to_file)
dump_button.place(x=20, y=0, width=260)
restore_button = Button(dump_lf, text="Restore from file to this cassette...", command=load_from_file)
restore_button.place(x=290, y=0, width=260)

updates_lf = LabelFrame(root, text="Updates", width=MAIN_WINDOW_WIDTH - PADDING*2, height=HEIGHT_CONNECT_LF*1.2)
updates_lf.place(x=PADDING, y=290)

def check_app_update():
    update_result = check_update.get_pc_app_update_status(THIS_VERSION_NUMBER)
    if update_result == 0:
        app_update_str_label.config(text='This app (' + str(THIS_VERSION_NUMBER) + '): Up to date', fg='black', bg='gray95')
        app_update_str_label.unbind("<Button-1>")
    elif update_result == 1:
        app_update_str_label.config(text='This app (' + str(THIS_VERSION_NUMBER) + '): Update available! Click me!', fg='black', bg='orange', cursor="hand2")
        app_update_str_label.bind("<Button-1>", update_click)
    elif update_result == 2:
        app_update_str_label.config(text='This app (' + str(THIS_VERSION_NUMBER) + '): Unknown', fg='black', bg='gray95')
        app_update_str_label.unbind("<Button-1>")

app_update_str_label = Label(master=updates_lf)
app_update_str_label.place(x=PADDING, y=5)
app_update_str_label.config(text='This app: Unknown', fg='black', bg='gray95')
app_update_str_label.unbind("<Button-1>")

def check_firmware_update():
    global fw_ver_string
    fw_ver_string = fw_ver_string.replace('FW V', '').replace('\r', '').replace('\n', '')
    fw_result = check_update.get_firmware_update_status(fw_ver_string)
    if fw_result == 0:
        firmware_update_str_label.config(text='Firmware (' + str(fw_ver_string) +'): Up to date', fg='black',bg='gray95')
        firmware_update_str_label.unbind("<Button-1>")
    elif fw_result == 1:
        firmware_update_str_label.config(text='Firmware (' + str(fw_ver_string) +'): Update available! Click me!', fg='black', bg='orange', cursor="hand2")
        firmware_update_str_label.bind("<Button-1>", fw_update_click)
    else:
        firmware_update_str_label.config(text='Firmware: Unknown', fg='black', bg='gray95')
        firmware_update_str_label.unbind("<Button-1>")

firmware_update_str_label = Label(master=updates_lf)
firmware_update_str_label.place(x=300, y=5)
firmware_update_str_label.config(text='Firmware: Unknown', fg='black', bg='gray95')
firmware_update_str_label.unbind("<Button-1>")

def update_click(event):
    webbrowser.open('https://github.com/dekuNukem/daytripper/releases')

serial_dropdown_refresh()

check_app_update()

root.mainloop()
