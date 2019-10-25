FROM python:3.7
ENV PYTHONUNBUFFERED 1
ADD requirements.txt /aioVextractor/
##  添加国内镜像源
RUN mkdir -p /root/.pip/ \
ADD pip.conf /root/.pip/pip.conf
WORKDIR /aioVextractor
RUN apt-get update \
    && apt-get install -y ffmpeg \
    && pip3 install --upgrade pip \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN pip3 install -r requirements.txt \
ENV PATH=/usr/local/bin:/usr/local/sbin:/sbin:/bin:/usr/sbin:/usr/bin:/root/bin