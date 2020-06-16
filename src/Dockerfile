ARG ALPINE_VERSION=3.11
ARG PYTHON_VERSION=3.8.3
FROM python:${PYTHON_VERSION}-alpine${ALPINE_VERSION}

RUN apk update \
    && apk add libc-dev \
        gcc \
        linux-headers \
        gnupg

ENV PYTHONUNBUFFERED=1
ADD ./requirements.txt /src/requirements.txt

WORKDIR /src
COPY . /src

RUN pip install wheel
RUN pip wheel -w /wheelhouse -r /src/requirements.txt
RUN pip install -r  /src/requirements.txt

RUN chmod u+x entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]

CMD [ "--help" ]
