FROM osgeo/gdal:alpine-normal-3.1.3
RUN mkdir /app
WORKDIR /app
RUN apk update -q --no-cache \
    && apk add -q --no-cache python3 py3-pip \
    && apk --no-cache add sudo
RUN python -m pip install --upgrade pip
COPY . .
RUN pip install --ignore-installed requests urllib3 -t /app
RUN pip install -r ./requirements.txt -t /app
RUN apk del py3-pip
ENV PYTHONPATH=${PYTHONPATH}:'/usr/lib/python3.8/site-packages/urllib3/exceptions.py:/app'
RUN python3 /app/confd/generate-config.py
RUN mkdir /app/src/outputs
WORKDIR /app/src/
CMD ["python3", "app.py"]
