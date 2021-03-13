FROM ubuntu:latest
RUN apt update && apt install -y curl
RUN curl -fsSL https://deb.nodesource.com/setup_15.x | bash -
RUN apt install -y supervisor nodejs software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install -y python3.9 python3-pip

RUN mkdir -p /var/log/supervisor
RUN mkdir -p /app
WORKDIR /app

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY trader/ ./
COPY web/ ./
COPY requirements.txt ./
COPY main.py ./

RUN pip3 install -r requirements.txt
RUN npm install

CMD ["/usr/bin/supervisord"]