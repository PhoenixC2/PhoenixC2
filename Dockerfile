FROM python

EXPOSE 8080
WORKDIR /tmp

COPY . . 

RUN pip install .

ENTRYPOINT ["python", "-m", "phoenixc2"]

CMD ["server"]
