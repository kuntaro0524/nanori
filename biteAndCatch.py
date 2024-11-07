import CUI 
import time

if __name__ == "__main__":
    cui = CUI.CUI()

    # フィルムを掴む位置へ移動すること
    cui.omukaeFJouku()
    time.sleep(10.0)
    cui.omukaePrep()
    time.sleep(1.0)

    cui.cut_all()
    time.sleep(1.0)

    cui.omukaeFJouku()





