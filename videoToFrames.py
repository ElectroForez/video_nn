import cv2
import glob
import os
import sys
import re
from datetime import datetime
from moviepy.editor import *

def video_to_frames(path, toPath=None):
     if not os.path.exists(path):
       print(path + " not exists")
       return
     else:
        filename = path.split('/')[-1]
        if not toPath:
              toPath = filename + "_frames"
        if not os.path.exists(toPath):
              os.mkdir(toPath)
        if os.listdir(toPath):
              print('WARNING!!! Path is not empty. Files with the same name will be overwritten')

     t1 = datetime.now()
     videoCapture = cv2.VideoCapture()
     videoCapture.open(path)
     fps = videoCapture.get(cv2.CAP_PROP_FPS)
     frames = videoCapture.get(cv2.CAP_PROP_FRAME_COUNT)
     print("fps=", int(fps), "frames=", int(frames))
     for i in range(int(frames)):
          ret, frame = videoCapture.read()
          cv2.imwrite("%s/%d.jpg" % (toPath, i), frame)
     t2 = datetime.now()
     print('time cost = ', t2 - t1)

     with open(toPath + '/info.txt', 'w') as infoFile:
         infoFile.write(str(int(fps))  + '\n')
         infoFile.write(filename + '\n')
         infoFile.write(str(int(frames)))
     try:
        audioclip = AudioFileClip(path)
        print(audioclip.duration)
        audioclip.write_audiofile(toPath + '/audio.mp3')
     except:
         print('video without audio')
video_to_frames(*sys.argv[1:])
# extractAudio(sys.argv[2], 'barabans.mp3')