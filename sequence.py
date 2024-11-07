import CUI 
import time


if __name__ == "__main__":
    cui = CUI.CUI()

    # フィルムを掴む位置へ移動すること
    cui.grabFilmJouku()
    time.sleep(10.0)
    cui.moveFilmZ()
    time.sleep(5.0)
    # フィルムを掴んで持ち上げる
    #cui.grabFilmSurface()

    # フィルムをA1へ持っていく
    cui.moveto('E1')
    time.sleep(10.0)
    #cui.moveto('B1')
    #time.sleep(10.0)
    #cui.moveto('H7')

    # Fアームを迎え上空へ移動
    cui.omukaeFJouku()
    time.sleep(10.0)
    # Fアームを迎えポジションへ
    cui.omukaeF()
    time.sleep(10.0)
    cui.omukaePrep()
    time.sleep(5.0)

    # Cut 5sec
    cui.cut_all()
    time.sleep(10.0)

    # Fアームを再び上空へ
    cui.omukaeFJouku()
    time.sleep(5.0)

    # Fアームをホルダーへ
    cui.filmJouku()
    time.sleep(15.0)

    # ホルダーへフィルムを取り付ける
    cui.attachFilm()
    time.sleep(10.0)
