FROM python:3.12-slim-bookworm AS build
LABEL maintainer="darius.stefan@opensips.org"

RUN apt update && apt install -y git

WORKDIR /usr/src
RUN git clone https://github.com/OpenSIPS/SIPssert.git &&\
    cd SIPssert &&\
    python3 setup.py install

FROM python:3.12-slim-bookworm AS sipssert
LABEL maintainer="darius.stefan@opensips.org"

RUN apt update && apt install -y tcpdump

COPY --from=build /usr/local/bin/sipssert /usr/local/bin/sipssert
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

ENTRYPOINT ["sipssert"]

