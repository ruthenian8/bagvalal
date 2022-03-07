FROM ubuntu:20.04

LABEL maintainer="ruthenian8@gmail.com"

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt update
RUN apt install -y git
RUN apt install -y python3
RUN apt install -y python3-pip
RUN apt install -y python3-dev
RUN apt install -y curl
RUN ["curl -sS https://apertium.projectjj.com/apt/install-nightly.sh | sudo bash"]
RUN apt install hfst -y

WORKDIR .
COPY . .

RUN pip3 install bs4
RUN pip3 install pandas
RUN make merged.tr.hfstol
CMD ["bash"]