#Mono8データライブ表示の場合
#opencv-python利用
camera = neoapi.Cam()
camera.Connect()
while cv2.waitKey(1) != 27 :
	buffer = camera.GetImage()
	mat_buffer = buffer.GetNPArray()
	cv2.imshow("", mat_buffer)
