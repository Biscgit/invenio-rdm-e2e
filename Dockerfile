FROM docker:27.5-cli

ENV INVENIO_BRANCH="master"
ENV PYTHON_VERSION="3.9"

RUN apk add --update --no-cache \
    bash \
    build-base \
    cairo \
    curl \
    gcc \
    git \
    libffi-dev \
    make \
    nodejs \
    npm \
    openssl-dev \
    sqlite-dev \
    zlib-dev

RUN curl -fsSL https://pyenv.run | bash
ENV PATH="/root/.pyenv/bin/:$PATH"

RUN pyenv install $PYTHON_VERSION && \
    pyenv global $PYTHON_VERSION && \
    pyenv exec pip install setuptools invenio-cli

WORKDIR /code
RUN git clone https://github.com/inveniosoftware/invenio-app-rdm.git && \
    cd invenio-app-rdm && \
    git checkout ${INVENIO_BRANCH} && \
    pyenv exec pip install -e .

WORKDIR ./website
RUN pyenv exec invenio-cli init rdm --no-input

WORKDIR ./my-site
RUN pyenv exec invenio-cli install

EXPOSE 5000
# CMD ["pyenv", "exec", "invenio-cli", "services", "setup", \
#      "&&", "pyenv", "exec", "invenio-cli", "run"]