# Raspberry Pi irregation system

### GPIO: the need for **sudo**

The python scripts must be either run as root to access the GPIO, or the pi user granted access to them. If using the former method you'll want to allow a couple enviroment variables set in `/etc/environment` to be available to `sudo`.

Note: add the following line to `/etc/sudoers` by using `visudo`

```sh
Defaults env_keep += "JABBER_ID JABBER_PASSWORD FORCASTIO_KEY"
```

