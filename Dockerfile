FROM forez/realsr-ncnn-vulkan

ENV TZ=Europe/Moscow
ENV BASICSR_EXT=True
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update && apt upgrade -y
WORKDIR /usr/src/
RUN git clone https://github.com/ElectroForez/video_nn.git
WORKDIR /usr/src/video_nn
RUN apt install python3-pip ffmpeg libsm6 libxext6 -y
RUN pip install -r requirments.txt
ENV IS_DOCKER=1
ENTRYPOINT ["python3", "video_nn.py"]

