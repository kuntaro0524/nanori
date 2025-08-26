import Nanori

if __name__ == '__main__':
    nanori_axis = Nanori.Nanori('192.168.163.102',7777)
    nanori_valve = Nanori.Nanori('192.168.163.101',7777)

    channel = 0
    #nanori_valve.getHoldStatus(channel)
    nanori_valve.setHoldStatus(channel,"on")