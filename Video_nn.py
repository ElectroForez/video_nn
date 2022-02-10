import cv2
import os
import sys
import subprocess
import glob
from datetime import datetime
from moviepy.editor import AudioFileClip

class Video_nn:
    def improveVideo(self, pathToVideo, pathToUpdatedVideo='untitled.avi', *argsRealsr):#Function to improve the video
        filename = pathToVideo.split('/')[-1]#take filename
        if pathToUpdatedVideo.split('/')[-1].count('.') == 0:#check path it's file or directory
            if not os.path.exists(pathToUpdatedVideo):
                os.mkdir(pathToUpdatedVideo)
            directory = pathToUpdatedVideo
            pathToUpdatedVideo += '/untitled.avi'#it's path for a future file
        else:
            directory = pathToVideo.split(filename)[0]

        pathToFragments = filename.replace('.', '-') + '_fragments'
        pathToUpdatedFragments = filename.replace('.', '-') + '_updated_fragments'
        pathToUpdatedVideoWithoutAudio = 'UWOA_' + filename

        if directory:
            pathToFragments = directory + '/' + pathToFragments
            pathToUpdatedFragments = directory + '/' + pathToUpdatedFragments
            pathToUpdatedVideoWithoutAudio = directory + '/' + pathToUpdatedVideoWithoutAudio
        for path in [pathToFragments, pathToUpdatedFragments]:
            if not os.path.exists(path):
                os.mkdir(path)
        if self.videoToFragments(pathToVideo, pathToFragments) != 0:
            print('Error on function video to fragments')
            return -1

        subprocess.run(['cp', pathToFragments + '/info.txt', pathToFragments + '/audio.mp3', pathToUpdatedFragments])

        finish_returnCode = self.useRealsr(pathToFragments, pathToUpdatedFragments, *argsRealsr)

        if finish_returnCode != 0:
            print('Error on upscaling frames')
            return -1

        if self.glueFrames(pathToUpdatedFragments, pathToUpdatedVideoWithoutAudio) != 0:
            print('Error on glue frames')
            return -1
        if self.addAudio(pathToUpdatedVideoWithoutAudio, pathToFragments + '/audio.mp3', pathToUpdatedVideo) != 0:
            print('Error on adding audio')
            return -1

        return 0

    def useRealsr(self, pathToInput, pathToOutput, *argsRealsr, pathToRealsr='./realsr-ncnn-vulkan/realsr-ncnn-vulkan'):
        t1 = datetime.now()
        finish = subprocess.run([pathToRealsr, '-i', pathToInput, '-o', pathToOutput, *argsRealsr])
        t2 = datetime.now()
        print('time cost realsr =', t2 - t1)
        return finish.returncode

    def videoToFragments(self, path, toPath=None):
        # check paths
        if not os.path.exists(path):
            print(path + " not exists")
            return
        elif os.path.isdir(path):
            print(toPath + " is not file")
            return
        elif toPath and toPath.split('/')[-1].count('.') > 0:
            print(toPath + " is not directory")
            return

        filename = path.split('/')[-1]

        if not toPath:
            toPath = filename.replace('.', '-') + "_fragments"
        if not os.path.exists(toPath):
            os.mkdir(toPath)
        if os.listdir(toPath):
            print('WARNING!!! Path for fragments is not empty. Files with the same name will be overwritten')

        t1 = datetime.now()
        videoCapture = cv2.VideoCapture()
        videoCapture.open(path)
        fps = videoCapture.get(cv2.CAP_PROP_FPS)
        frames = videoCapture.get(cv2.CAP_PROP_FRAME_COUNT)
        print("fps=", int(fps), "frames=", int(frames))

        count_frames = 0 #sometimes the wrong number of frames is displayed. Recalculation just in case
        for i in range(int(frames)):
            ret, frame = videoCapture.read()
            if ret:
                count_frames += 1
                cv2.imwrite("%s/%d.png" % (toPath, i), frame)
        t2 = datetime.now()
        if count_frames != frames:
            frames = count_frames
        print('time cost  = ', t2 - t1)

        # create a txt file with additional info for processing by other programs
        with open(toPath + '/info.txt', 'w') as infoFile:
            infoFile.write(str(int(fps)) + '\n')  # fps
            infoFile.write(filename + '\n')  # filename
            infoFile.write(str(int(frames)))  # frames
        # catching audio
        try:
            audioclip = AudioFileClip(path)
            audioclip.write_audiofile(toPath + '/audio.mp3')
            audioclip.close()
        except:
            print('video without audio')

        return 0

    def glueFrames(self, pathToSrc, pathToVideo='untitled.avi', codec='h264', fps=30, *argsFffmpeg, photoExtension='png'):
        frames = glob.glob(pathToSrc + '/*.' + photoExtension)
        if len(frames) == 0:
            print(f'Frames with extension {photoExtension} not found')
            return
        frameSize = cv2.imread(frames[0]).shape[1::-1]
        filename = 'untitled.avi'

        if os.path.exists(pathToSrc + '/info.txt'):
            with open(pathToSrc + '/info.txt', 'r') as infoFile:
                try:
                    fps = int(infoFile.readline())
                    filename = 'UpdWOA_' + infoFile.readline().strip()#Updated without audio
                    countFrames = int(infoFile.readline())
                    if countFrames != len(frames):
                        print('The number of files in info.txt does not match the actual')
                except:
                    print("Bad info.txt")
        else:
            print("WARNING!!! info.txt not exists. It's true path?")

        if pathToVideo.split('/')[-1].count('.') == 0:
            pathToVideo += '/' + filename

        t1 = datetime.now()

        finish = subprocess.run(['ffmpeg', '-start_number', '1', '-r', str(fps), '-i', pathToSrc + '/%d.png', '-vcodec', codec, '-y', *argsFffmpeg, pathToVideo])

        t2 = datetime.now()
        print('time cost qlue =', t2 - t1)

        # addAudio(pathToVideo, pathToSrc + '/audio.mp3', 'videos/finale_barabans.avi')#потом надо будет
        return finish.returncode

    def addAudio(self, pathToVideo, pathToAudio, newName=None):
        if not newName:
            newName = 'UPDATED_' + pathToVideo.split('/')[-1]
        if pathToVideo in (newName, pathToAudio):
            print('Files with same name')
            return
        t1 = datetime.now()
        finish = subprocess.run(['ffmpeg', '-i', pathToAudio, '-i', pathToVideo, '-codec', 'copy', '-y', newName])
        t2 = datetime.now()
        print('time cost add audio = ', t2 -t1)
        return finish.returncode

if __name__ == '__main__':
    video_nn = Video_nn()
    # video_nn.improveVideo('videos/crop_barabans.mp4', 'videos/cropped_fragments')
    video_nn.improveVideo(*sys.argv[1:])