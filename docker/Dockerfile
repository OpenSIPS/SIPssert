FROM python:3.12-bookworm
LABEL maintainer="darius.stefan@opensips.org"

RUN apt update && apt install -y tcpdump &&\
    pip install --upgrade pip &&\
    pip install pyyaml &&\
    git clone https://github.com/OpenSIPS/SIPssert.git &&\
    cd SIPssert &&\
    python3 setup.py install &&\
    cd ..

ENTRYPOINT ["sipssert"]

