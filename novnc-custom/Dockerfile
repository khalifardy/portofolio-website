FROM alpine:latest

RUN apk add --no-cache \
    bash \
    python3 \
    py3-numpy \
    git \
    openssl \
    && rm -rf /var/cache/apk/*

WORKDIR /opt

RUN git clone --depth 1 https://github.com/novnc/noVNC.git && \
    git clone --depth 1 https://github.com/novnc/websockify.git noVNC/utils/websockify

WORKDIR /opt/noVNC

EXPOSE 8080

# Gunakan IP docker0 langsung instead of host.docker.internal
CMD ["./utils/novnc_proxy", "--listen", "8080", "--vnc", "172.17.0.1:15900"]