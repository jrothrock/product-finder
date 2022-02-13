# pull official base image
FROM python:3.10.2-slim-buster as base

# set work directory
WORKDIR /usr/src/app


FROM base as poetry
RUN pip install --upgrade pip
RUN pip install poetry==1.1.12
COPY poetry.lock pyproject.toml /usr/src/app/
RUN poetry export -o requirements.txt --without-hashes

FROM base as build
COPY --from=poetry /usr/src/app/requirements.txt /tmp/requirements.txt
RUN python -m venv .venv && \
    .venv/bin/pip install --upgrade pip && \
    .venv/bin/pip install 'wheel==0.36.2' && \
    .venv/bin/pip install -r /tmp/requirements.txt

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

FROM base as runtime
WORKDIR /usr/src/app

# copy project
COPY . /usr/src/app/
# remove local .venv, if one
RUN rm -rf /usr/src/app/.venv

ENV PATH=/usr/src/app/.venv/bin:$PATH
COPY --from=build /usr/src/app/.venv /usr/src/app/.venv
