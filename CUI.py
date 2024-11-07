import Nanori
import sys
import time
import numpy as np
import pandas as pd

class Well():
    def __init__(self):
        # A1 coordinates
        a1_x = 9473
        a1_y = 20982
        # H7 coordinates
        h7_x = 22850
        h7_y = 36805
        # A1 x_start: SY1
        self.x_start = a1_x
        self.x_end = h7_x
        self.x_points = 7
        # A1
        self.y_start = a1_y
        # H7
        self.y_end = h7_y
        self.y_points = 8
        self.isInit=False

    def create_well_coordinates_table(self):
        import pandas as pd

        x_coordinates = np.linspace(self.x_start, self.x_end, self.x_points)

        # 縦方向（Y座標）の計算
        y_coordinates = np.linspace(self.y_start, self.y_end, self.y_points)
        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        cols = [str(i) for i in range(1, 8)]

        # DataFrameの作成
        coordinate_dict = {}
        for i, y in enumerate(y_coordinates):
            for j, x in enumerate(x_coordinates):
                coordinate_name = f"{rows[i]}{cols[j]}"
                coordinate_dict[coordinate_name] = (x, y)

        self.coordinates_df = pd.DataFrame.from_dict(coordinate_dict, orient='index', columns=['X', 'Y'])
        return self.coordinates_df

class CUI:
    def __init__(self):
        self.nanori = Nanori.Nanori('192.168.163.102',7777)
        self.nanori_valve=Nanori.Nanori('192.168.163.101',7777)

        # well position calculation
        well = Well()
        self.well_coordinates = well.create_well_coordinates_table()

        # dictionary axis
        self.axis_list=['s-x', 's-y1', 's-y2', 's-z1', 's-z2', 'f-x', 'f-y', 'f-z']

    def grabFilmJouku(self):
        # arm1 z1 = 22000
        z1_index=self.axis_list.index('s-z1')
        self.nanori.moveAbs(z1_index, 20000)
        # arm1 y1 = 19856
        y1_index = self.axis_list.index('s-y1')
        self.nanori.moveAbs(y1_index, 19856)
        # arm1 s-x = 8000
        x_index = self.axis_list.index('s-x')
        self.nanori.moveAbs(x_index, 8000)

    def moveFilmZ(self):
        # z1 = 24000 2024.11.06
        z1_index=self.axis_list.index('s-z1')
        self.nanori.moveAbs(z1_index, 24000)

    def grabFilmSurface(self):
        # arm1 y1 = 19856
        y1_index = self.axis_list.index('s-y1')
        self.nanori.moveAbs(y1_index, 19856)
        # arm1 s-x = 8000
        x_index = self.axis_list.index('s-x')
        self.nanori.moveAbs(x_index, 8000)
        # arm1 z1 = 24000
        z1_index=self.axis_list.index('s-z1')
        self.nanori.moveAbs(z1_index, 24500)
        # valve 2 'on'
        self.nanori_valve.setHoldStatus(3, 'off')
        # valve 3 'on'
        self.nanori_valve.setHoldStatus(4, 'off')
        time.sleep(10)
        # arm1 z1 = 23800
        z1_index=self.axis_list.index('s-z1')
        self.nanori.moveAbs(z1_index, 24000)

    def releaseFilm(self):
        self.nanori_valve.setHoldStatus(3, 'on')
        self.nanori_valve.setHoldStatus(4, 'on')

    def moveto(self,position_text):
        x,y = self.well_coordinates.loc[position_text]
        # x coordinate: 's-x'
        x_index = self.axis_list.index('s-x')
        self.nanori.moveAbs(x_index, x)
        # y coordinate: 's-y1'
        y_index = self.axis_list.index('s-y1')
        self.nanori.moveAbs(y_index, y)

    def omukaeFJouku(self):
        # arm F-z = 15852
        z_index = self.axis_list.index('f-z')
        self.nanori.moveAbs(z_index, 21229)
        # arm F-y = 24563
        y_index = self.axis_list.index('f-y')
        self.nanori.moveAbs(y_index, 24563)
        # arm F-x = 3236
        x_index = self.axis_list.index('f-x')
        self.nanori.moveAbs(x_index, 3236)
        time.sleep(2.0)

    def omukaeF(self):
        #omukaeFJouku()
        # arm F-z = 22607+ 5377
        value = 22607+5377
        z_index = self.axis_list.index('f-z')
        self.nanori.moveAbs(z_index, value)
        time.sleep(3.0)

    def armVacuumOn(self):
        self.nanori_valve.setHoldStatus(0, 'off')

    def armVacuumOff(self):
        self.nanori_valve.setHoldStatus(0, 'on')

    def omukaePrep(self):
        self.omukaeF()
        # valve 1 を開ける (channel 0)
        self.armVacuumOn()

    def evacuateF(self):
        # arm F-z = 15852 -> 21229
        z_index = self.axis_list.index('f-z')
        self.nanori.moveAbs(z_index, 21229)
        # arm F-y = 12000
        y_index = self.axis_list.index('f-y')
        self.nanori.moveAbs(y_index, 12000)
        # arm F-x = 3236
        x_index = self.axis_list.index('f-x')    
        self.nanori.moveAbs(x_index, 3236)
    
    def cut_all(self):
        # cut timer から秒数を取得
        cut_timer = 5.0
        # reset ch11
        self.nanori_valve.setHoldStatus(11, 'on')
        time.sleep(0.5)
        self.nanori_valve.setHoldStatus(10, 'off')
        time.sleep(0.5)
        self.nanori_valve.setHoldStatus(10, 'on')

        time.sleep(cut_timer)
        print(self.nanori_valve.isLSon("CWLS",10))
        time.sleep(0.1)
        print(self.nanori_valve.isLSon("CCWLS",10))

        self.nanori_valve.setHoldStatus(11, 'off')
        time.sleep(0.5)
        self.nanori_valve.setHoldStatus(11, 'on')
        print(self.nanori_valve.isLSon("CCWLS",10))

    def filmJouku(self):
        # F-x = 36067
        x_index = self.axis_list.index('f-x')
        self.nanori.moveAbs(x_index, 36067)
        # F-y = 24792
        y_index = self.axis_list.index('f-y')
        self.nanori.moveAbs(y_index, 24792)
        # F-z = 15852 -> 15852+5377
        z_index = self.axis_list.index('f-z')
        self.nanori.moveAbs(z_index, 21229)

    def attachFilm(self):
        # F-x = 36067
        x_index = self.axis_list.index('f-x')
        self.nanori.moveAbs(x_index, 36067)
        # F-y = 24792
        y_index = self.axis_list.index('f-y')
        self.nanori.moveAbs(y_index, 24792)
        # F-z = 20223 -> 25600
        z_index = self.axis_list.index('f-z')
        self.nanori.moveAbs(z_index, 25600)
        time.sleep(1.0)
        # release gas
        self.armVacuumOff()
        time.sleep(5.0)
        # evacuation
        self.filmJouku()

    #nanori_balve.setHoldStatus(3, 'on')
    #channel = sys.argv[1]
    #value = int(sys.argv[2])
    #moveto(sys.argv[1])
    #evacuateF()
    #time.sleep(5)
    #omukaeFJouku()
    #time.sleep(10)
    #omukaeF()
    #time.sleep(5)
    #omukaeFJouku()
    #time.sleep(5)
    #filmJouku()
    #time.sleep(10)
    #attachFilm()
    #time.sleep(3)
    #filmJouku()
    #filmJouku()
    #evacuateF()