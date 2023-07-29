#!/bin/bash
wget https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-linux-amd64 -O /usr/bin/mkcert

chmod +x /usr/bin/mkcert

rm -r mkcert
mkdir mkcert
CAROOT=./mkcert mkcert -cert-file mkcert/cert.pem -key-file mkcert/key.pem localhost 127.0.0.1 ::1
CAROOT=./mkcert mkcert -install

chmod go=rx mkcert/cert.pem mkcert/key.pem

echo "Add rootCA.pem certicate to your web browser"
echo ""
echo "https://docs.vmware.com/en/VMware-Adapter-for-SAP-Landscape-Management/2.1.0/Installation-and-Administration-Guide-for-VLA-Administrators/GUID-0CED691F-79D3-43A4-B90D-CD97650C13A0.html"
