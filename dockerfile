FROM python:3.11-slim-buster

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update -y && apt-get upgrade -y \
    && apt-get install -y make wget nano vim \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

RUN addgroup --uid 1000 styloexport
RUN adduser --disabled-login --ingroup styloexport --uid 1000 styloexport
USER styloexport:styloexport

WORKDIR /usr/stylo-export

ENV VIRTUAL_ENV=/usr/stylo-export/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN mkdir ./static ./tmp
RUN pip install gunicorn
COPY --chown=styloexport:styloexport Makefile setup.* .
COPY --chown=styloexport:styloexport styloexport ./styloexport
COPY --chown=styloexport:styloexport templates ./templates
COPY --chown=styloexport:styloexport styles ./styles
COPY --chown=pandocapi:pandocapi README.md ./README.md
COPY --chown=pandocapi:pandocapi pyproject.toml ./pyproject.toml
RUN make install
COPY --chown=styloexport:styloexport .envdocker ./.env

EXPOSE 8001
CMD ["make", "production"]
