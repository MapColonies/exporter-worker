FROM osgeo/gdal:alpine-normal-3.1.3
RUN mkdir /app
WORKDIR /app
COPY requirements.txt ./
RUN apk update -q --no-cache \
    && apk add -q --no-cache python3 py3-pip
RUN pip3 install -r ./requirements.txt -t /app
COPY . .
RUN apk del py3-pip
ENV PYTHONPATH=${PYTHONPATH}:'/app'
RUN python3 /app/confd/generate-config.py --environment production
WORKDIR /app/
RUN chmod +x start.sh
CMD ["sh", "start.sh"]
