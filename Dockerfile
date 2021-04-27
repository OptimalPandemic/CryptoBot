FROM ubuntu:latest
RUN apt update && apt install -y curl nginx
RUN curl -fsSL https://deb.nodesource.com/setup_15.x | bash -
RUN apt install -y supervisor nodejs software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt install -y python3 python3-pip

RUN mkdir -p /var/log/supervisor
RUN mkdir -p /app
WORKDIR /app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
COPY web/frontend/package.json /app/web/frontend/package.json

WORKDIR /app/web/frontend
RUN npm install

WORKDIR /app
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY trader/ ./trader
COPY web/ ./web
COPY main.py ./
COPY utils.py ./
COPY config.yml ./

RUN python3 utils.py --config config.yml
COPY web/nginx.conf /etc/nginx/nginx.conf

CMD ["/usr/bin/supervisord"]
EXPOSE 80