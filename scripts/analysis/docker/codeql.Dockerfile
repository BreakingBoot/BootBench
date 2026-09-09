# CodeQL CLI plus a C/C++ toolchain, so a bootloader can be built and analysed
# in one place. The host needs neither CodeQL nor autotools.
FROM ubuntu:24.04

ARG CODEQL_VERSION=v2.26.4
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential autoconf automake libtool pkg-config bison flex \
        git curl ca-certificates unzip xz-utils \
        python3 zlib1g-dev libssl-dev uuid-dev \
        nasm iasl gcc-multilib bc \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL -o /tmp/codeql.zip \
      "https://github.com/github/codeql-cli-binaries/releases/download/${CODEQL_VERSION}/codeql-linux64.zip" \
 && unzip -q /tmp/codeql.zip -d /opt && rm /tmp/codeql.zip \
 && /opt/codeql/codeql --version

# The query packs live in the github/codeql submodule, mounted at /queries.
ENV PATH="/opt/codeql:${PATH}"
WORKDIR /src
