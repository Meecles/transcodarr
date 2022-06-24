apt-get update
/usr/local/bin/python -m pip install --upgrade pip
export IN_DOCKER=true
pip3 install -r requirements.txt
apt-get update && apt-get install -y software-properties-common
apt-get update && apt-get install -y handbrake-cli handbrake
mkdir -p /root/.ssh
cp /root/keys/* /root/.ssh/
chown root:root /root/.ssh/*
chmod 600 /root/.ssh/*

