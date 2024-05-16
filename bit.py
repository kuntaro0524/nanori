def is_bit_set(hex_value, bit_position):
    # 16進数の値を10進数に変換
    decimal_value = int(hex_value, 16)
    
    # 指定されたビットが立っているかを判定
    return (decimal_value & (1 << bit_position)) != 0

def checkBit(switch, hex_value):
    # bitの情報は
    # 0: holdの状態
    # 1: HPLS
    # 2: CCWLS
    # 3: CWLS 
    switch = switch.upper()
    bit_dict = {"HOLD": 0, "HPLS": 1, "CCWLS": 2, "CWLS": 3}
    target_bit = bit_dict[switch]
    # print(target_bit)
    is_set = is_bit_set(hex_value, target_bit)
    return is_set

# テスト
import sys
hex_value = sys.argv[1]  # 16進数のAは10進数の10、2進数では1010
bit_position = 1

bits = [0,1,2,3]

for this_bit in bits:
    if is_bit_set(hex_value, this_bit):
        print(f"Bit {this_bit} is 1 in {hex_value}.")
    else:
        print(f"Bit {this_bit} is 0 in {hex_value}.")

isCWLS=checkBit("CWLS", hex_value)
isCCWLS=checkBit("CCWLS", hex_value)

print("CWLS:", isCWLS)
print("CCWLS:", isCCWLS)