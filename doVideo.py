import cv2
import glob
import os
import sys
from moviepy.editor import *
def doVideo(pathToSrc, filename=None, fps=30, extension='png', codec='DIVX'):
    frames = glob.glob(pathToSrc + '/*.' + extension)
    # print(src)
    frameSize = cv2.imread(frames[0]).shape[1::-1]
    print(frameSize)
    if os.path.exists(pathToSrc + '/info.txt'):
        with open(pathToSrc + '/info.txt', 'r') as infoFile:
            fps = int(infoFile.readline())
            if not filename:
                filename = 'Updated_' + infoFile.readline().strip()
    if not filename:
        filename = 'untitled.avi'
    out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*codec), fps, frameSize)
    for frame in sorted(frames,
                           key=lambda x: int(x.split('/')[-1].split('.')[0])):
        img = cv2.imread(frame)
        out.write(img)
    print(filename)
    audioclip = AudioFileClip(pathToSrc + "/audio.mp3")
    out.release()
    # new_audioclip = CompositeAudioClip([audioclip])
    # out.audio = new_audioclip
    # videoclip.write_videofile("new_filename.mp4")
print(sys.argv)
doVideo(*sys.argv[1:], extension='jpg')