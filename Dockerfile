FROM python:3

COPY ./app.py /code/
COPY ./requirements.txt /code/
COPY ./templates /code/templates/
WORKDIR /code

RUN pip install --no-cache-dir -Ur /code/requirements.txt \
    && pip install --no-cache-dir -U uwsgi

RUN apt-get update && apt-get install -y texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended texlive-lang-german lmodern texlive-fonts-extra && apt-get clean

EXPOSE 5000
ENTRYPOINT [ "uwsgi", "--wsgi-file", "app.py", "--callable", "app", "--enable-threads", "--http", ":5000" ]
