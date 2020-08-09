# docker-rclone-serve

This image proxies any rclone-supported backend and serves this as an SFTP server (using `rclone serve`).
By proxying a back-end, you can share it with multiple devices or users without having to share the credentials directly.

## User / backend configuration

Create a yaml file which defines a map of users to their auth details and backend config. To work out the available backend keys, configure it with rclone and look at the produced config file (e.g. `rclone config -config /path/to/file`).
Because it's yaml you can use anchors to re-use bits, e.g. to have users share the same backend. To help with this, any keys starting with underscore are ignored (so users starting with underscore won't work, sorry).

A user's auth details may contain `public_key` and/or `pass`. User passwords are just plaintext so you should really use key pairs.

Mount this file at `/config/users.yaml`.

Example
```yaml
_backend: &backend
    type: sftp
    host: sftp.example.com
    user: sftpuser
    pass: sftpsecret
    _obscure: pass

user1:
    pass: topsecret
    backend:
        <<: *backend
        _root: /user1

user2:
    public_key: AAAAB3NzaC1yc2EAAAADAQABAAABAQDuwESFdAe14hVS6omeyX7edcJQdf
    backend:
        <<: *backend
        _root: /user2    
```

## Running

You may pass any additional arguments to rclone via Docker commands (see example below).

### Volumes

| Volume | Purpose
|-       |-
| `/config` | Contains config file and cache

### Ports

| Port | Purpose
|- |-
| `2022` | SFTP (SSH, without console) port

## Example

Running directly
```
docker run -v /host-path/config:/config -p 2022:2022 rclone-serve
```

You may pass any additional arguments to rclone via Docker commands. For example,
you might like to generate and use a static server key file (though rclone will generate one at start-up and cache this if you don't).
```
docker run -v /host-path/config:/config -p 2022:2022 rclone-serve --key /config/id_rsa
```
