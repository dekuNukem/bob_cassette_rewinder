import sys
import time
import serial
from datetime import datetime

def iso8601_utc_now():
    ret = datetime.utcnow().isoformat(sep='T')
    return (ret[:19] + "Z").replace(':', '-')

if(len(sys.argv) < 2):
    print(__file__ + ' serial_port')
    exit()

print("Opening", sys.argv[1], '...')

ser = serial.Serial(sys.argv[1], 115200)

bin_dict = {}

while 1:
    this_line = ser.readline().decode('utf-8')
    print(this_line)
    if 'bobdump' in this_line:
        addr = int(this_line.split(' ')[1])
        data = int(this_line.split(' ')[2])
        bin_dict[addr] = data
    if 'done' in this_line.lower():
        break;

ser.close()

if len(bin_dict) != 256:
    print('Wrong size! exiting...')

byte_list = []
for i in range(len(bin_dict)):
    byte_list.append(bin_dict[i])

print(bin_dict)
print(bytes(byte_list))

filename = input("\n\nfilename?\n")
if len(filename) > 0:
    filename = '_' + filename
with open(iso8601_utc_now() + filename + ".bin", 'wb') as outfile:
    outfile.write(bytes(byte_list))