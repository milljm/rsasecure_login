#!/bin/bash
set -eu
cp -R rsasecure_login $SP_DIR/
cd ${PREFIX}/bin
ln -s $SP_DIR/rsasecure_login/rsasecure_login.py rsasecure_login
cat > $SP_DIR/rsasecure_login-$PKG_VERSION.egg-info <<FAKE_EGG
Metadata-Version: 2.1
Name: RSASecureID Login
Version: $PKG_VERSION
Summary: RSASecurID Protected Channel Conda Helper
Platform: UNKNOWN
FAKE_EGG

# Prevent race condition during quick builds (odd that this works/is needed)
sleep 5
