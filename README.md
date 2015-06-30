# Raspberry Pi irregation system

### GPIO: the need for **sudo**

The python scripts must be either run as root to access the GPIO, or the pi user granted access to them. If using the former method you'll want to allow a couple enviroment variables set in `/etc/environment` to be available to `sudo`.

Note: add the following line to `/etc/sudoers` by using `visudo`

```sh
Defaults env_keep += "JABBER_ID JABBER_PASSWORD FORCASTIO_KEY"
```


For the later method of allowing the `pi` user access to the GPIO, try one of these methods: https://www.raspberrypi.org/forums/viewtopic.php?f=44&t=73924
https://github.com/quick2wire/quick2wire-gpio-admin
