FROM python:3

RUN mkdir /storj_data
ADD https://raw.githubusercontent.com/ReneSmeekes/storj_earnings/master/earnings.py /usr/local/bin/

VOLUME /storj_data

ENTRYPOINT [ "python3", "/usr/local/bin/earnings.py", "/storj_data" ]
