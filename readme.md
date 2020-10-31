# docker-rclone-serve

[![GitHub last commit](https://img.shields.io/github/last-commit/jonohill/docker-rclone-serve?label=github+last+commit)](https://github.com/jonohill/docker-rclone-serve) [![Docker Image Version (latest semver)](https://img.shields.io/docker/v/jonoh/rclone-serve?label=docker+hub&sort=semver)](https://hub.docker.com/r/jonoh/rclone-serve)

This image proxies any rclone-supported backend and serves this as an SFTP server (using `rclone serve`).
By proxying a back-end, you can share it with multiple devices or users without having to share the backend credentials.

## rclone configuration

The rclone configuration file defines the available backends and is read from `$RCLONE_AUTH_PROXY_BACKENDS` (by default `/config/rclone.conf`).
You can create this file using rclone: `rclone config --config rclone.conf`

## User configuration

The user configuration file defines users' names and credentials, which backend the user has access to, and which backend path the user can access. 
It is read from `$RCLONE_AUTH_PROXY_USERS` (by default `/config/users.conf`).

Check [rclone's docs](https://rclone.org/commands/rclone_serve_sftp/#auth-proxy) to understand better how `rclone serve` handles these details.

Example:
```
[user1]
public_key = AAAAC3NzaC1lZDI1NTE5AAAAIGIn18t0VonWAGDpsiIuZApik8erVceVNjPX0mT4Z4Sy
             AAAAC3NzaC1lZDI1NTE5AAAAILTfzZi3i3DqJQjW9H6XhseA0B5cg7F0+zUtgxBia87g
backend = my_gdrive_backend
root = /

[user2]
password = topsecret
backend = my_onedrive_backend
root = /user2
```

Passwords are stored as plaintext so try to use public keys instead (these are SSH public keys). A user may have more than one public key as shown above.
The `backend` should match what you configured in `rclone.conf`.

## Details

### Environment Variables

| Name | Default | Purpose
|-     |-        |-
| `RCLONE_AUTH_PROXY_BACKENDS` | `/config/rclone.conf` | Path to rclone configuration file.
| `RCLONE_AUTH_PROXY_USERS` | `/config/users.conf` | Path to user configuration file.

### Volumes

| Volume | Purpose
|-       |-
| `/config` | Contains config file and cache.

### Ports

| Port | Purpose
|- |-
| `2022` | SFTP (SSH, without console)

## Example

Running directly
```
docker run -v /host-path/config:/config -p 2022:2022 rclone-serve
```

You may pass any additional arguments to rclone via Docker commands. 
For example, you might like to generate and use a static server key file (though rclone will generate one at start-up and cache this if you don't).
```
docker run -v /host-path/config:/config -p 2022:2022 rclone-serve --key /config/id_rsa
```

## Tags

Tags mirror the rclone version. The image is rebuilt when a new rclone image becomes available.
