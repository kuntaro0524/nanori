import neoapi
import cv2
import time
import matplotlib.pyplot as plt

camera = neoapi.Cam()
camera.Connect('10.178.163.104')
#It can be name, or serial number, or ip adress of your camera

camera.f.ExposureTime.Set(20537)
camera.DisableChunk()
    
camera.SetImageBufferCount()      
camera.SetImageBufferCycleCount()  

try:
    camera.f.PixelFormat.Set(neoapi.PixelFormat_BGR8)
    print("using RGB")
except neoapi.FeatureAccessException:
    camera.f.PixelFormat.Set(neoapi.PixelFormat_Mono8)

camera.f.TriggerMode.value = neoapi.TriggerMode_On
