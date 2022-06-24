import os
import re
import time
from threading import Thread

import config
from utils.db_config import db


class ProgressThread(Thread):

    def __init__(self, video_item):
        self.interrupted = False
        self.last_print = None
        self.video_item = video_item
        self.log_regex = r'(?:(?:[Ea-z]{8}:\stask\s1\sof\s1,\s)+([0-9]{1,3}.[0-9]{1,3})+(?:\s%\s\()+([0-9]{1,4}.[0-9]{1,3})+(?:\sfps,\savg\s)+([0-9]{1,4}.[0-9]{1,3})+(?:\sfps,\sETA\s+([0-9]{2,}h[0-9]{1,2}m[0-9]{1,2}s)))'
        self.no_data = False
        Thread.__init__(self)

    def update_db(self, percent, fps, avg, eta, elapsed):
        item = db["processing"].find_one({"_id": self.video_item["_id"]})
        if item is None:
            print("[Warning] Database entry not found, rogue transcode?")
            return
        if "progress" not in item:
            item["progress"] = {
                "percent": percent,
                "fps": fps,
                "avg": avg,
                "eta": eta,
                "elapsed": elapsed
            }
        p = item["progress"]
        p["percent"] = percent
        p["fps"] = fps
        p["avg"] = avg
        p["eta"] = eta
        p["elapsed"] = elapsed
        item["progress"] = p
        db["processing"].find_one_and_replace({"_id": item["_id"]}, item)

    def testfor_print(self, perc, last_perc, last_print_time):
        if last_print_time is None:
            return True
        now = time.time()
        threshold = 4.99
        time_threshold = 30.0
        if now - last_print_time >= time_threshold or perc == 0.0 or perc >= last_perc + threshold:
            return True
        return False

    def prog(self, perc, last_perc, message):
        try:
            last_perc = float(last_perc)
            perc = float(perc)
            self.last_print = float(self.last_print)
        except Exception as e:
            return True
        if self.testfor_print(perc, last_perc, self.last_print):
            print(message, flush=True)
            self.last_print = time.time()
            return True
        return False

    def run(self) -> None:
        self.pause(2)
        last_perc = 0.0
        pperc = 0.0
        while not self.interrupted:
            with open("handbrake.log") as f:
                content = f.readlines()
            content = [x.strip() for x in content]
            reg = self.log_regex
            latest_match = None
            largest_match = None
            largest_match_p = 0.0
            for line in content:
                line = line.replace("\r", "").replace("\n", "")
                match = re.search(reg, line)
                if match is not None:
                    gps = match.groups()
                    perc, fps, avg, eta = gps[0], gps[1], gps[2], gps[3]
                    try:
                        perc_f = float(perc)
                        latest_match = "Progress: {}% FPS: {}, Avg: {}, Eta: {}".format(perc, fps, avg, eta)
                        if perc_f > largest_match_p:
                            largest_match = {
                                "perc_f": perc_f,
                                "perc_s": perc,
                                "fps": fps,
                                "avg": avg,
                                "eta": eta
                            }
                    except Exception as e:
                        print("Error parsing data: using latest match instead")
                        latest_match = "Progress: {}% FPS: {}, Avg: {}, Eta: {}".format(perc, fps, avg, eta)
                        print(latest_match)
                        pperc = perc
                        self.update_db(perc, fps, avg, eta, "N/A")
            if largest_match is not None:
                perc = largest_match["perc_s"]
                fps = largest_match["fps"]
                avg = largest_match["avg"]
                eta = largest_match["eta"]
                self.update_db(perc, fps, avg, eta, "N/A")

            if latest_match is None:
                if not self.no_data:
                    print("No progress data...", flush=True)
                    self.no_data = True
            else:
                printed = self.prog(pperc, last_perc, latest_match)
                if printed:
                    last_perc = pperc
                self.no_data = False
            self.pause(3)

    def pause(self, seconds):
        for second in range(0, seconds):
            if self.interrupted:
                return
            time.sleep(1)

    def interrupt(self):
        self.interrupted = True


def transcode(file, video_item):
    preset = "Fast 1080p30"
    is_docker = config.get_value("IS_DOCKER", not_none=True) == "true"
    in_folder = "/media/in/" if is_docker else "in/"
    out_folder = "/media/out/" if is_docker else "out/"
    ext = file.split(".")[len(file.split(".")) - 1]
    in_filename = file.split("/")[len(file.split("/")) - 1].replace("(", "\\(").replace(")", "\\)")
    out_filename = in_filename.replace(".{}".format(ext), ".mp4")

    infile = "{}{}".format(in_folder, in_filename)
    outfile = "{}{}".format(out_folder, out_filename)

    transcode_threads = config.get_value("TRANSCODE_CORES")
    cmd = "HandBrakeCLI -i {} -o {} '{}'".format(infile, outfile, preset)
    if transcode_threads is not None:
        opts = "-C {}".format(transcode_threads)
        cmd = "HandBrakeCLI -i {} -o {} {} '{}'".format(infile, outfile, opts, preset)
    os.system("touch handbrake.log handbrake.err.log")
    cmd = "{} 1> handbrake.log 2> handbrake.err.log".format(cmd)
    progress_thread = ProgressThread(video_item)
    progress_thread.start()
    os.system(cmd)
    progress_thread.interrupt()
    progress_thread.join()
    os.system("rm handbrake.log handbrake.err.log")
    return outfile, out_filename

