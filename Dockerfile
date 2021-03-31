FROM ubuntu:latest
RUN apt update && apt install -y curl nginx
RUN curl -fsSL https://deb.nodesource.com/setup_15.x | bash -
RUN apt install -y supervisor nodejs software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install -y python3.9 python3-pip

RUN mkdir -p /var/log/supervisor
RUN mkdir -p /app
WORKDIR /app
ENV PYTHONPATH=/usr/local/lib/python3.8/dist-packages:/app

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY trader/ ./trader
COPY web/ ./web
COPY requirements.txt ./
COPY main.py ./
COPY web/nginx.conf /etc/nginx/nginx.conf

RUN pip3 install -r requirements.txt
RUN npm install

CMD ["/usr/bin/supervisord"]
EXPOSE 80