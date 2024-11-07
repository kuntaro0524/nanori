import CUI 
import time

if __name__ == "__main__":
    cui = CUI.CUI()

    # フィルムを掴む位置へ移動すること
    cui.grabFilmJouku()
    time.sleep(10.0)
    cui.grabFilmSurface()