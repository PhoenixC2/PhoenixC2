FROM python:3.10

COPY . .

RUN python3 -m pip install -r requirements.txt

RUN python3 install.py /usr/share/

CMD [ "pfserver", "-a", "0.0.0.0" ]