FROM rclone/rclone:1.72.0

RUN apk add --no-cache \
    python3

COPY auth-proxy.py /usr/local/bin/auth-proxy

ENV RCLONE_AUTH_PROXY_BACKENDS=/config/rclone.conf
ENV RCLONE_AUTH_PROXY_USERS=/config/users.conf
ENV RCLONE_OPTIONS=

EXPOSE 2022

ENTRYPOINT [ "sh", "-c", "rclone --config $RCLONE_AUTH_PROXY_BACKENDS $RCLONE_OPTIONS serve sftp --cache-dir /config/cache --auth-proxy auth-proxy --addr :2022" ]
