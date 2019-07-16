
FROM nvidia/cuda:9.0-cudnn7-devel-ubuntu16.04

RUN echo "deb http://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1604/x86_64 /" > /etc/apt/sources.list.d/nvidia-ml.list

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        cmake \
        curl \
        git \
        nginx \
        supervisor \
        wget && \
        rm -rf /var/lib/apt/lists/*

ENV PYTHON_VERSION=3.6
RUN curl -o ~/miniconda.sh -O  https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh  && \
    chmod +x ~/miniconda.sh && \
    ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda create -y --name py$PYTHON_VERSION python=$PYTHON_VERSION && \
    /opt/conda/bin/conda clean -ya
ENV PATH /opt/conda/envs/py$PYTHON_VERSION/bin:$PATH
ENV LD_LIBRARY_PATH /opt/conda/envs/py$PYTHON_VERSION/lib:/usr/local/cuda/lib64/:$LD_LIBRARY_PATH
ENV PYTHONPATH /code/:$PYTHONPATH

RUN mkdir /app
WORKDIR /app
ADD process_images_from_queue.py /app
ADD style_transfer.py /app
ADD main.py /app
ADD util.py /app
ADD requirements.txt /app
ADD constants.py /app

RUN pip install --no-cache-dir -r requirements.txt

RUN rm /opt/conda/envs/py3.6/lib/python3.6/site-packages/azure/servicebus/constants.py
RUN cp constants.py /opt/conda/envs/py3.6/lib/python3.6/site-packages/azure/servicebus/

CMD ["python", "main.py"]
