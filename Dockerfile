FROM rclone/rclone

RUN apk add --no-cache \
    python3 \
    py3-pip

COPY auth-proxy/requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt
COPY auth-proxy/auth-proxy.py /usr/local/bin/auth-proxy

EXPOSE 2022

ENTRYPOINT [ "rclone", "serve", "sftp", "--cache-dir", "/config/cache", "--auth-proxy", "auth-proxy", "--addr", ":2022" ]
