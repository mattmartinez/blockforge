#!/bin/sh
mine stop
wget http://smos-linux.org/upgrade/sgminer.pl
wget http://smos-linux.org/upgrade/sgminer2.pl
rm -rf /opt/bamt/gpumon
mv sgminer2.pl /opt/bamt/gpumon
rm -rf /opt/bamt/common.pl
mv sgminer.pl /opt/bamt/common.pl
sleep 5
cd /opt/miners/
rm -rf cgminer
git clone https://github.com/veox/sgminer
cp /opt/ADL/include/* /opt/miners/sgminer/ADL_SDK/
cd /opt/miners/sgminer/
./autogen.sh
sleep 5
make clean
sleep 5
CFLAGS="-O2 -Wall -march=native -I /opt/AMDAPP/include/" LDFLAGS="-L/opt/AMDAPP/lib/x86" ./configure --enable-scrypt --enable-opencl --bindir="/opt/miners/sgminer" --prefix="/usr/local/bin"
sleep 5
make
sleep 5
rm -rf /root/sgminer.sh
clear
echo "sgminer 4.0.0 installed."
echo "SMOS-Linux.org"
echo "Now reboot your rig, and start mining"
