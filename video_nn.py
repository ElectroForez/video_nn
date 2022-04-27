import time
import shutil
import cv2
import os
import subprocess
import glob
from datetime import datetime
from moviepy.editor import AudioFileClip
import argparse


def print_timecost(func):
    def wrapper(*args, **kwargs):
        t1 = datetime.now()
        statuscode = func(*args, **kwargs)
        t2 = datetime.now()
        print(f'time cost {func.__name__} =', t2 - t1)
        return statuscode
    return wrapper


@print_timecost
def improve_video(videofile, upd_videofile='untitled.avi', *args_realsr, func_upscale):
    """
    improve quality of video using frame-by-frame processing.
    func_upscale processes frames
    """
    func_upscale = print_timecost(func_upscale)
    if not os.path.exists(videofile):
        print(f'File {videofile} not found')
        return -1
    if os.path.isdir(videofile):
        print(f'{videofile} it is a directory')
        return -1
    filename = videofile.split('/')[-1]  # take filename
    if upd_videofile.split('/')[-1].count('.') == 0:  # check path that it's directory
        if not upd_videofile.endswith('/'):
            upd_videofile += '/'
        if not os.path.exists(upd_videofile):
            os.mkdir(upd_videofile)
            subprocess.run(f'chown -R 1000:1000 {upd_videofile}'.split(), capture_output=True)
        directory = upd_videofile
        upd_videofile += 'untitled.avi'  # it's path for a future file
    else:
        r_slash_ind = upd_videofile.rfind('/')
        if r_slash_ind == -1:
            directory = '.'
        else:
            directory = upd_videofile[:r_slash_ind]
    if not os.path.exists(directory):
        os.mkdir(directory)
    if not directory.endswith('/'):
        directory += '/'

    fragments_path = filename.replace('.', '-') + '_fragments/'
    upd_fragments_path = 'Updated_' + fragments_path
    upd_videofile_WOA = 'UWOA_' + filename  # UWOA - Updated without audio

    if directory:
        fragments_path = directory + fragments_path
        upd_fragments_path = directory + upd_fragments_path
        upd_videofile_WOA = directory + upd_videofile_WOA

    for path in [fragments_path, upd_fragments_path]:
        if not os.path.exists(path):
            os.mkdir(path)
    try:
        return_code_frag = video_to_fragments(videofile, fragments_path)
        if return_code_frag != 0:
            print('Error on function video to fragments')
            return -1

        # copy info and audio of video to path with updated fragments
        subprocess.run(['cp', fragments_path + 'info.txt', fragments_path + 'audio.mp3', upd_fragments_path],
                       capture_output=True)

        return_code_upscale = func_upscale(fragments_path, upd_fragments_path, *args_realsr)
        if return_code_upscale != 0:
            print('Error on upscaling frames')
            return -1

        return_code_glue = glue_frames(upd_fragments_path, upd_videofile_WOA)
        if return_code_glue != 0:
            print('Error on glue frames')
            return -1

        if not os.path.exists(fragments_path + 'audio.mp3'):
            print('Audio not found')
            os.rename(upd_videofile_WOA, upd_videofile)
        else:
            return_code_audio = add_audio(upd_videofile_WOA, fragments_path + 'audio.mp3', upd_videofile)
            if return_code_audio != 0:
                print('Error on adding audio')
                return -1
    finally:
        # chown for convenient work with Docker
        if os.environ.get('IS_DOCKER'):
            for path in [fragments_path, upd_fragments_path, upd_videofile_WOA, upd_videofile]:
                subprocess.run(f'chown -R 1000:1000 {path}'.split(), capture_output=True)
    return 0


@print_timecost
def use_realsr(input_path, output_path, *args_realsr):
    """up-scaling frames"""
    realsr_path = os.environ.get('REALSR_PATH')
    if realsr_path is None:
        realsr_path = './realsr-ncnn-vulkan/realsr-ncnn-vulkan'
    finish = subprocess.run([realsr_path, '-i', input_path, '-o', output_path, *args_realsr])
    # finish = subprocess.run(['cp', input_path, output_path])
    # time.sleep(3)
    return finish.returncode


@print_timecost
def video_to_fragments(video_path, output_path=None):
    """split video into frames and audio, & write some info in info.txt"""
    # check paths
    if output_path.endswith('/'):
        output_path = output_path[:-1]

    if not os.path.exists(video_path):
        print(video_path + " not exists")
        return -1
    elif os.path.isdir(video_path):
        print(video_path + " is not file")
        return -1
    elif output_path and output_path.split('/')[-1].count('.') > 0:
        print(output_path + " is not directory")
        return - 1

    output_path += '/'
    filename = video_path.split('/')[-1]

    if not output_path:
        output_path = filename.replace('.', '-') + "_fragments"
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    if os.listdir(output_path):
        print(f'WARNING!!! Path for fragments {output_path} is not empty. This folder will be deleted')
        shutil.rmtree(output_path)
        os.mkdir(output_path)

    videoCapture = cv2.VideoCapture()
    videoCapture.open(video_path)
    fps = videoCapture.get(cv2.CAP_PROP_FPS)
    frames = videoCapture.get(cv2.CAP_PROP_FRAME_COUNT)
    print("fps=", int(fps), "frames=", int(frames))

    count_frames = 0  # sometimes the wrong number of frames is displayed. Recalculation just in case
    for i in range(int(frames)):
        ret, frame = videoCapture.read()
        if ret:
            count_frames += 1
            cv2.imwrite("%s/%d.jpg" % (output_path, i), frame)
    if count_frames != frames:
        frames = count_frames

    # catching audio
    audioclip = AudioFileClip(video_path)
    if audioclip.reader.infos['audio_found']:
        audioclip.write_audiofile(output_path + 'audio.mp3')
        with_audio = True
    else:
        print('Video without audio')
        with_audio = False
    audioclip.close()

    # create a txt file with additional info for processing by other programs
    with open(output_path + 'info.txt', 'w') as infoFile:
        infoFile.write(str(int(fps)) + '\n')  # fps
        infoFile.write(filename + '\n')  # filename
        infoFile.write(str(int(frames)) + '\n')  # frames
        infoFile.write(str(int(with_audio)))  # with(out) audio

    return 0


@print_timecost
def glue_frames(src_path, videofile='untitled.avi', codec='h264', fps=30, *args_ffmpeg, photo_extenstion='png'):
    if not src_path.endswith('/'):
        src_path += '/'
    frames = glob.glob(src_path + '*.' + photo_extenstion)
    if len(frames) == 0:
        print(f'Frames with extension {photo_extenstion} not found')
        return
    filename = 'untitled.avi'

    if os.path.exists(src_path + 'info.txt'):
        with open(src_path + 'info.txt', 'r') as infoFile:
            try:
                fps = int(infoFile.readline())
                filename = 'UpdWOA_' + infoFile.readline().strip()  # Updated without audio
                count_frames = int(infoFile.readline())
                if count_frames != len(frames):
                    print('The number of files in info.txt does not match the actual')
            except ValueError:
                print("Bad info.txt")
    else:
        print("WARNING!!! info.txt not exists. It's true path?")
        fps = 30

    if videofile.split('/')[-1].count('.') == 0:
        videofile += '/' + filename

    finish = subprocess.run(
        ['ffmpeg', '-start_number', '1', '-r', str(fps), '-i', src_path + '%d.png', '-vcodec', codec, '-y',
         *args_ffmpeg, videofile])

    return finish.returncode


@print_timecost
def add_audio(videofile, audio_path, new_name=None):
    if not new_name:
        new_name = 'UPDATED_' + videofile.split('/')[-1]
    if videofile in (new_name, audio_path):
        print('Files with same name')
        return
    finish = subprocess.run(['ffmpeg', '-i', audio_path, '-i', videofile, '-codec', 'copy', '-y', new_name])
    return finish.returncode


if __name__ == '__main__':
    video_dir = '/mounted/' if os.environ.get('IS_DOCKER') else ''
    parser = argparse.ArgumentParser(prog='Improve video', description='Use realsr for processing video frame by frame')
    parser.add_argument('-i', '--input', type=str, help='Input path for video', required=True)
    parser.add_argument('-o', '--output', type=str, default='untitled.avi',
                        help='Output path for video. Temporary files will be stored in the same path.')
    parser.add_argument('-r', '--realsr', metavar='REALSR ARGS', default='', type=str)
    args = parser.parse_args()

    input_video = video_dir + args.input
    output_video = video_dir + args.output
    args_realsr = args.realsr

    improve_video(input_video, output_video, *args_realsr.split(), func_upscale=use_realsr)
