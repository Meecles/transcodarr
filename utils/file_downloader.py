import os

import config


def download_file_from_volume(filepath, movie_volume, tv_volume):
    is_docker = config.get_value("IS_DOCKER", not_none=True) == "true"
    base_path = "/media/copy" if is_docker else config.get_value("DOWNLOAD_FILE_PREFIX", not_none=True)
    radarr_path = config.get_value("DOWNLOAD_RADARR_PATH", not_none=True)
    sonarr_path = config.get_value("DOWNLOAD_SONARR_PATH", not_none=True)
    if radarr_path is not None and filepath.startswith("{}/".format(radarr_path)):
        filepath = filepath.replace("{}/".format(radarr_path), "{}/radarr/".format(base_path))
    if sonarr_path is not None and filepath.startswith("{}/".format(sonarr_path)):
        filepath = filepath.replace("{}/".format(sonarr_path), "{}/sonarr/".format(base_path))
    filepath = filepath.replace("//", "/")
    outfilepath = "/media/in" if is_docker else "./in/"
    escaped_filepath = filepath.replace("(", "\\(").replace(")", "\\)").replace(" ", "\\ ")
    copy_cmd = "cp {} {}".format(escaped_filepath, outfilepath)
    os.system(copy_cmd)
    return True


def download_file_from_ssh(filepath):
    is_docker = config.get_value("IS_DOCKER", not_none=True) == "true"
    base_path = config.get_value("DOWNLOAD_FILE_PREFIX", not_none=True)
    radarr_path = config.get_value("DOWNLOAD_RADARR_PATH", not_none=True)
    sonarr_path = config.get_value("DOWNLOAD_SONARR_PATH", not_none=True)
    if radarr_path is not None and filepath.startswith("{}/".format(radarr_path)):
        filepath = filepath.replace("{}/".format(radarr_path), "{}/radarr/".format(base_path))
    if sonarr_path is not None and filepath.startswith("{}/".format(sonarr_path)):
        filepath = filepath.replace("{}/".format(sonarr_path), "{}/sonarr/".format(base_path))
    outfilepath = "/media/in" if is_docker else "./in/"
    escaped_filepath = filepath.replace("(", "\\(").replace(")", "\\)")
    scp_cmd = None
    if not is_docker:
        ssh_connect_string = config.get_value("SSH_DOWNLOAD_CONNECT_STRING", not_none=True)
        if not ssh_connect_string.endswith(":"):
            ssh_connect_string = "{}:".format(ssh_connect_string)
            scp_cmd = "scp '{}{}' {}".format(ssh_connect_string, escaped_filepath, outfilepath)
    else:
        ip = config.get_value("DOWNLOAD_SSH_IP")
        private_key = config.get_value("DOWNLOAD_SSH_PRIVATE_KEY")
        username = config.get_value("DOWNLOAD_SSH_USERNAME")
        if ip is None or private_key is None or username is None:
            print("[Error] Failed to download file, no ssh connect details")
            return False
        ssh_connect_string = "-i /root/.ssh/{} '{}@{}:".format(private_key, username, ip)
        scp_cmd = "scp {}{}' {}".format(ssh_connect_string, escaped_filepath, outfilepath)
    if scp_cmd is not None:
        os.system(scp_cmd)
        return True
    return False


def download_file(filepath):
    unprocessable_chars = ["'", " "]
    for ch in unprocessable_chars:
        if ch in filepath:
            return False
    movie_volume = config.get_value("DOWNLOAD_MOVIE_VOLUME")
    tv_volume = config.get_value("DOWNLOAD_TV_VOLUME")
    if movie_volume is None or tv_volume is None:
        return download_file_from_ssh(filepath)
    return download_file_from_volume(filepath, movie_volume, tv_volume)
