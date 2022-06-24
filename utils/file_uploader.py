import os

import config
from api import plex


def test_ssh():
    key = config.get_value("UPLOAD_SSH_PRIVATE_KEY")
    ip = config.get_value("UPLOAD_SSH_IP")
    username = config.get_value("UPLOAD_SSH_USERNAME")
    cmd = "ssh -i /root/.ssh/{} -o \"StrictHostKeyChecking=no\" {}@{} 'echo connected'".format(key, username, ip)
    os.system(cmd)


def upload_tv_show(item, outfile, out_filename):
    ip = config.get_value("UPLOAD_SSH_IP")
    is_docker = config.get_value("IS_DOCKER", not_none=True) == "true"
    key = config.get_value("UPLOAD_SSH_PRIVATE_KEY")
    username = config.get_value("UPLOAD_SSH_USERNAME")
    remote_path = config.get_value("UPLOAD_SSH_TV_PATH")

    if remote_path is None:
        print("[Error] Unable to upload file, no remote path")
        return False
    connect_string = None
    if ip is None or key is None or username is None:
        connect_string = config.get_value("UPLOAD_SSH_CONNECT_STRING")
        if connect_string is None:
            print("[Error] Unable to upload file, no ssh connect details.")
            return False

    if not remote_path.endswith("/"):
        remote_path = "{}/".format(remote_path)

    if connect_string is None:
        connect_string = "-i {} {}@{}".format(key, username, ip)

    up_path = plex.get_show_upload_path(item)

    connect_string = None
    if ip is None or key is None or username is None:
        connect_string = config.get_value("UPLOAD_SSH_CONNECT_STRING")
        if connect_string is None:
            print("[Error] Unable to upload file, no ssh connect details.")
            return False

    key_loc = None
    if key is not None:
        key_loc = "/root/.ssh/{}".format(key) if is_docker else key

    if connect_string is None:
        connect_string = "-i {} {}@{}".format(key_loc, username, ip)

    mkdir = "ssh {} 'mkdir -p {}{}'".format(connect_string, remote_path, up_path)
    os.system(mkdir)

    cred_string = "-i {} ".format(key_loc) if key is not None else ""
    upload_path = "{}{}/".format(remote_path, up_path)
    up_connect = config.get_value("UPLOAD_SSH_CONNECT_STRING")
    if up_connect is None:
        up_connect = "{}@{}".format(username, ip)
    if not up_connect.endswith(":"):
        up_connect = "{}:".format(up_connect)

    upload_cmd = "scp {}{} '{}{}'".format(cred_string, outfile, up_connect, upload_path)
    os.system(upload_cmd)

    return True

def upload_movie(item, outfile, out_filename):
    is_docker = config.get_value("IS_DOCKER", not_none=True) == "true"
    ip = config.get_value("UPLOAD_SSH_IP")
    key = config.get_value("UPLOAD_SSH_PRIVATE_KEY")
    username = config.get_value("UPLOAD_SSH_USERNAME")
    remote_path = config.get_value("UPLOAD_SSH_MOVIE_PATH")
    if remote_path is None:
        print("[Error] Unable to upload file, no remote path")
        return False
    connect_string = None
    if ip is None or key is None or username is None:
        connect_string = config.get_value("UPLOAD_SSH_CONNECT_STRING")
        if connect_string is None:
            print("[Error] Unable to upload file, no ssh connect details.")
            return False

    if not remote_path.endswith("/"):
        remote_path = "{}/".format(remote_path)

    key_loc = None
    if key is not None:
        key_loc = "/root/.ssh/{}".format(key) if is_docker else key

    if connect_string is None:
        connect_string = "-i {} {}@{}".format(key_loc, username, ip)

    encompassing_folder = out_filename.replace(".mp4", "")
    mkdir = "ssh {} 'mkdir -p {}{}'".format(connect_string, remote_path, encompassing_folder)
    os.system(mkdir)

    cred_string = "-i {} ".format(key_loc) if key is not None else ""
    upload_path = "{}{}/".format(remote_path, encompassing_folder)
    up_connect = config.get_value("UPLOAD_SSH_CONNECT_STRING")
    if up_connect is None:
        up_connect = "{}@{}".format(username, ip)
    if not up_connect.endswith(":"):
        up_connect = "{}:".format(up_connect)
    upload_cmd = "scp {}{} '{}{}'".format(cred_string, outfile, up_connect, upload_path)
    os.system(upload_cmd)
    return True

