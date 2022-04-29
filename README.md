# video_nn
the video_nn functions is designed for video processing using neural networks. Based on the neural network [realsr-ncnn-vulkan](https://github.com/nihui/realsr-ncnn-vulkan)

[Docker](https://hub.docker.com/repository/docker/forez/video_nn)
# requirments
opencv-python==4.5.5.62

moviepy==1.0.3

ffmpeg
# install
with already installed realsr-ncnn-vulkan
```
git clone https://github.com/ElectroForez/video_nn.git
pip install -r video_nn/requirments.txt
sudo apt install ffmpeg
```
# usage
```
export REALSR_PATH=YOUR_REALSR_PATH
$ python3 video_nn.py --help
usage: Improve video [-h] -i INPUT [-o OUTPUT] [-r REALSR ARGS]

Use realsr for processing video frame by frame

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input path for video
  -o OUTPUT, --output OUTPUT
                        Output path for video. Temporary files will be stored in the same path.
  -r REALSR ARGS, --realsr REALSR ARGS

```
# example
```
export REALSR_PATH="/home/vladt/realsr-ncnn-vulkan/realsr-ncnn-vulkan"
$ python3 video_nn.py -i /home/vladt/video_proc/upbar.mp4 -o /home/vladt/video_proc/UpdBar/updated_video.mp4 -r "-s 4"
```
