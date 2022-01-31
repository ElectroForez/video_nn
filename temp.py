import cv2
video = cv2.VideoCapture('new_new.mp4')
print(video.get(cv2.CAP_PROP_F))