import Nanori
import sys
import time
import numpy as np
import pandas as pd

class Well():
    def __init__(self):
        self.x_start = 9468
        self.x_end = 22838
        self.x_points = 7
        self.y_start = 20967
        self.y_end = 36770
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

if __name__ == '__main__':
    nanori = Nanori.Nanori('192.168.163.102',7777)
    nanori_balve=Nanori.Nanori('192.168.163.101',7777)

    # well position calculation
    well = Well()
    well_coordinates = well.create_well_coordinates_table()

    # dictionary axis
    axis_list=['s-x', 's-y1', 's-y2', 's-z1', 's-z2', 'f-x', 'f-y', 'f-z']


    def grabFilmJouku():
        # arm1 z1 = 22000
        z1_index=axis_list.index('s-z1')
        nanori.moveAbs(z1_index, 20000)
        # arm1 y1 = 19856
        y1_index = axis_list.index('s-y1')
        nanori.moveAbs(y1_index, 19856)
        # arm1 s-x = 8000
        x_index = axis_list.index('s-x')
        nanori.moveAbs(x_index, 8000)

    def grabFilmSurface():
        # arm1 y1 = 19856
        y1_index = axis_list.index('s-y1')
        nanori.moveAbs(y1_index, 19856)
        # arm1 s-x = 8000
        x_index = axis_list.index('s-x')
        nanori.moveAbs(x_index, 8000)
        # arm1 z1 = 24000
        z1_index=axis_list.index('s-z1')
        nanori.moveAbs(z1_index, 24300)
        # valve 2 'on'
        nanori_balve.setHoldStatus(3, 'off')
        # valve 3 'on'
        nanori_balve.setHoldStatus(4, 'off')
        time.sleep(2)
        # arm1 z1 = 23800
        z1_index=axis_list.index('s-z1')
        nanori.moveAbs(z1_index, 23800)

    def releaseFilm():
        nanori_balve.setHoldStatus(3, 'on')
        nanori_balve.setHoldStatus(4, 'on')

    def moveto(position_text):
        x,y = well_coordinates.loc[position_text]
        # x coordinate: 's-x'
        x_index = axis_list.index('s-x')
        nanori.moveAbs(x_index, x)
        # y coordinate: 's-y1'
        y_index = axis_list.index('s-y1')
        nanori.moveAbs(y_index, y)

    def omukaeFJouku():
        # arm F-z = 15852
        z_index = axis_list.index('f-z')
        nanori.moveAbs(z_index, 21229)
        # arm F-y = 24563
        y_index = axis_list.index('f-y')
        nanori.moveAbs(y_index, 24563)
        # arm F-x = 3236
        x_index = axis_list.index('f-x')
        nanori.moveAbs(x_index, 3236)
        time.sleep(2.0)

    def omukaeF():
        #omukaeFJouku()
        # arm F-z = 22607+ 5377
        value = 22607+5377
        z_index = axis_list.index('f-z')
        nanori.moveAbs(z_index, value)
        time.sleep(3.0)

    def evacuateF():
        # arm F-z = 15852 -> 21229
        z_index = axis_list.index('f-z')
        nanori.moveAbs(z_index, 21229)
        # arm F-y = 12000
        y_index = axis_list.index('f-y')
        nanori.moveAbs(y_index, 12000)
        # arm F-x = 3236
        x_index = axis_list.index('f-x')    
        nanori.moveAbs(x_index, 3236)

    def filmJouku():
        # F-x = 36067
        x_index = axis_list.index('f-x')
        nanori.moveAbs(x_index, 36067)
        # F-y = 24792
        y_index = axis_list.index('f-y')
        nanori.moveAbs(y_index, 24792)
        # F-z = 15852 -> 15852+5377
        z_index = axis_list.index('f-z')
        nanori.moveAbs(z_index, 21229)

    def attachFilm():
        # F-x = 36067
        x_index = axis_list.index('f-x')
        nanori.moveAbs(x_index, 36067)
        # F-y = 24792
        y_index = axis_list.index('f-y')
        nanori.moveAbs(y_index, 24792)
        # F-z = 20223 -> 25600
        z_index = axis_list.index('f-z')
        nanori.moveAbs(z_index, 25600)

    # index
    #idx = axis_list.index(channel)
    #grabFilmJouku()
    grabFilmSurface()
    #grabFilmSurface()
    #releaseFilm()

    

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