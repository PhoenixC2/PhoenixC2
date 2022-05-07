FROM python:3.10

COPY . .

RUN pip install -r requirements.txt

RUN python install.py

CMD [ "pfserver", "-a", "0.0.0.0" ]