import cv2
codec = 'DIVX'
print(type(cv2.VideoWriter_fourcc(*codec)))
print(cv2.VideoWriter_fourcc(*codec))