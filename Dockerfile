FROM osgeo/gdal:alpine-normal-3.1.3
RUN mkdir /app
WORKDIR /app
RUN apk update -q --no-cache \
    && apk add -q --no-cache python3 py3-pip
COPY . .
RUN pip3 install -r ./requirements.txt
RUN apk del py3-pip
ENV PYTHONPATH=${PYTHONPATH}:'/app'
RUN python3 /app/confd/generate-config.py
RUN mkdir /app/src/outputs
WORKDIR /app/src
CMD ["python3", "main.py"]
