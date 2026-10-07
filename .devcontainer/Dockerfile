FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

ARG GITLEAKS_VERSION=8.30.1
ARG SONAR_SCANNER_VERSION=8.1.0.6389

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
        unzip \
        jq \
        python3 \
        python3-pip \
        openjdk-21-jdk-headless \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz" \
        | tar -xz -C /usr/local/bin gitleaks \
    && gitleaks version

RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh \
        | sh -s -- -b /usr/local/bin \
    && trivy --version

RUN pip3 install --break-system-packages --no-cache-dir \
        checkov \
        pre-commit \
        pytest \
        pytest-cov \
        coverage

RUN curl -sSL -o /tmp/sonar-scanner.zip \
        "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-${SONAR_SCANNER_VERSION}-linux-x64.zip" \
    && unzip -q /tmp/sonar-scanner.zip -d /opt \
    && rm /tmp/sonar-scanner.zip

ENV PATH="/opt/sonar-scanner-${SONAR_SCANNER_VERSION}-linux-x64/bin:${PATH}"

USER vscode
