# RSA SecurID Login

rsasecure_login authenticates a user to an RSA SecurID protected resource, and saves the cookie session for later use during normal Conda command operations.


## Install

For now, rsasecure_login is available via the Idaholab Conda channel:

```bash
conda config --add channels idaholab
conda install rsasecure_login
```

## Use

To use rsasecure_login, supply a URI in the form of server/channel name:

```bash
./rsasecure_login --server my_protected_server.com/channel
```
