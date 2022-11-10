FROM python

EXPOSE 8080
WORKDIR /tmp

COPY . . 

RUN pip install .

CMD ["pfserver", "--"