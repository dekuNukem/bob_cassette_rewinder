xxx = 0x4e

for x in range(0, 31):
  print(30 - x, hex(0x4e - x))

# for x in range(0, 16):
#     print(15 - x, hex(15 - x + 0x50))


"""
washes      value @
left        addr 0xa1

30          0x4e
.
.
.
16          0x40

15          0x5f
.
.
.
0           0x50


amusing values: 0x3f = 111 washes, 0x4f = 31 washes

"""