FROM forez/realsr-ncnn-vulkan

RUN apt update && apt upgrade -y
WORKDIR /usr/src/
RUN git clone https://github.com/ElectroForez/video_nn.git
WORKDIR /usr/src/video_nn
RUN apt install python3-pip -y
RUN pip install -r requirments.txt
ENV IS_DOCKER=1
ENTRYPOINT bash

