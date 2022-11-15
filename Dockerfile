FROM python

EXPOSE 8080
WORKDIR /tmp

COPY . . 

RUN pip install .

ENTRYPOINT ["pfserver", "-a", "0.0.0.0"]
