import cv2
import glob
import os
import sys
from moviepy.editor import *
import subprocess

def doVideo(pathToSrc, pathToVideo='untitled.avi', fps=30, extension='png', codec='DIVX'):
    frames = glob.glob(pathToSrc + '/*.' + extension)
    frameSize = cv2.imread(frames[0]).shape[1::-1]

    if os.path.exists(pathToSrc + '/info.txt'):
        with open(pathToSrc + '/info.txt', 'r') as infoFile:
            try:
                fps = int(infoFile.readline())
                orig_filename = 'Updated_' + infoFile.readline().strip()
            except:
                print("Bad info.txt")
    else:
        print("WARNING!!! info.txt not exsists. It's true path?")

    # if '.' in pathToVideo.split('/')[-1]:
    #     pathToVideo = pathToVideo.split('/')[-1]


        

    out = cv2.VideoWriter(pathToVideo, cv2.VideoWriter_fourcc(*codec), fps, frameSize)
    for frame in sorted(frames,
                           key=lambda x: int(x.split('/')[-1].split('.')[0])):
        img = cv2.imread(frame)
        out.write(img)
    out.release()

    addAudio(pathToVideo, pathToSrc + '/audio.mp3', )

def addAudio(pathToVideo, pathToAudio, newName=None):
    if not newName:
        newName = 'UPDATED_' + pathToVideo.split('/')[-1]
    if os.path.exists(pathToAudio):
        subprocess.run(['ffmpeg', '-i', pathToAudio, '-i', pathToVideo, '-codec', 'copy', '-y', pathToVideo + '/' + newName])

doVideo(*sys.argv[1:])