FROM python

WORKDIR /usr/src/bmstu_lab

COPY req.txt ./

RUN pip install -r req.txt