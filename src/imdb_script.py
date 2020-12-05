import os 
import shlex
import subprocess 
import parse
import time
import argparse


def parse_imdb(choice):
    src_dir = "../texts/IMDB/preprocessed/{}"

    log_dir = "imdb_failed_{}.log".format(choice)
    choice = choice.replace("_", "/")
    assert choice in [
        "test/pos", "test/neg", "train/pos", "train/neg"], "Illegal choice of data fold: {}".format(choice)

    if os.path.exists(log_dir):
        os.remove(log_dir)
    flog = open(log_dir, "a+")

    for fname in os.listdir(src_dir.format(choice)):
        start_time = time.time()
        full_fn = os.path.join(src_dir.format(choice), fname)
        output_dir = "IMDB/{}".format(choice)
        cmd = "python parse.py -g -t {} {}".format(output_dir, full_fn)

        pipe = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            stdout, stderr = pipe.communicate(timeout=180)
        except subprocess.TimeoutExpired:
            print ("RST parser timeout: {}".format(full_fn))
            flog.write(full_fn + "\n")
            flog.flush()
            continue

        if len(stderr) > 0:
            print ("Failed: {}".format(full_fn))
            flog.write(full_fn + "\n")
            flog.flush()
        else:
            print ("Done:   {} in {:.2f} seconds".format(full_fn, time.time() - start_time))
    
    flog.close()


if __name__ == "__main__":
    agp = argparse.ArgumentParser()
    agp.add_argument('--choice', type=str, default='train_pos')
    args = agp.parse_args()
    parse_imdb(args.choice)
