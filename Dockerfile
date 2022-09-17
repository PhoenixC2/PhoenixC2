FROM python

EXPOSE 8080
WORKDIR /tmp

COPY . . 

RUN python3 install.py -l "/Phoenix-Framework/" -p docker

RUN rm -rf /tmp/*

CMD ["python3", "/usr/bin/pfserver", "-a", "0.0.0.0", "-l", "/Phoenix-Framework/Server"]