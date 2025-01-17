FROM docker:27.5-cli

ENV INVENIO_BRANCH="master"

RUN apk add --update --no-cache python3 py3-virtualenv nodejs openssl \
    gcc \
    make \
    musl-dev \
    libffi-dev \
    openssl-dev \
    zlib-dev \
    bzip2-dev \
    xz-dev \
    readline-dev \
    sqlite-dev \
    gdbm-dev \
    ncurses-dev \
    linux-headers \
    git \
    cairo \
    cairo-dev \
    npm \
    build-base bash curl gcc patch zip openssl-dev linux-headers make cmake

RUN mkdir /code && chmod +rwx /code
WORKDIR /code

RUN python3 -m venv venv
ENV PATH="/code/venv/bin:$PATH"

RUN git clone https://github.com/inveniosoftware/invenio-app-rdm.git && \
    cd invenio-app-rdm && \
    git checkout ${INVENIO_BRANCH}
WORKDIR /code/invenio-app-rdm

RUN pip install .
RUN pip install invenio-cli

RUN curl -fsSL https://pyenv.run | bash
ENV PATH="/root/.pyenv/bin/:$PATH"

RUN invenio-cli init rdm --no-input
WORKDIR /code/invenio-app-rdm/my-site/

RUN pyenv install 3.9 && \
    pyenv global 3.9
RUN invenio-cli install

EXPOSE 5000
#CMD ["invenio-cli", "run"]
# CMD ["invenio-cli", "services", "setup", "&&", "invenio-cli", "run"]