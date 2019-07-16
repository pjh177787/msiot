
FROM continuumio/miniconda3

RUN mkdir /app
WORKDIR /app
ADD add_images_to_queue.py /app
ADD preprocess.py /app
ADD postprocess.py /app
ADD util.py /app
ADD main.py /app
ADD constants.py /app

RUN conda install -c conda-forge -y ffmpeg
RUN pip install azure
RUN pip install flask

RUN rm /opt/conda/lib/python3.7/site-packages/azure/servicebus/constants.py
RUN cp constants.py /opt/conda/lib/python3.7/site-packages/azure/servicebus/

CMD ["python", "main.py"]
