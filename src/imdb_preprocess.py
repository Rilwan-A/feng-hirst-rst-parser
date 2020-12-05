import os 
import re 
import time


def preprocess_imdb():
    folders = ["test/pos", "test/neg", "train/pos", "train/neg"]
    base_dir = "../texts/IMDB/aclImdb/{}"
    tgt_dir = "../texts/IMDB/preprocessed/{}"

    for fold in folders:
        start_time = time.time()
        if not os.path.isdir(tgt_dir.format(fold)):
            os.makedirs(tgt_dir.format(fold))
        for fname in os.listdir(base_dir.format(fold)):
            full_fn_in = os.path.join(base_dir.format(fold), fname)
            full_fn_out = os.path.join(tgt_dir.format(fold), fname)

            with open(full_fn_in, "r") as f:
                doc_str = f.read()

            proc_str = replace_br(doc_str)
            proc_str = add_space_after_sentence(proc_str)

            with open(full_fn_out, "w") as f:
                f.write(proc_str)

        print ("Done processing folder {} in {:.2f} seconds".format(fold, time.time() - start_time))


def replace_br(doc_str):
    doc_str = re.sub("<br />", " ", doc_str)
    return doc_str 


def add_space_after_sentence(doc_str):
    L = doc_str.split(".")
    L_proc = []
    for i in range(len(L)):
        if i > 0 and re.match("^[0-9]", L[i]) is not None:
            # L[i] starts with number. We shouldn't insert space before it.
            L_proc.append(L[i])
        elif L[i].startswith(" "):
            # There is already a space before L[i]. i.e., after the period.
            L_proc.append(L[i])
        else:
            L_proc.append(" " + L[i])
    return ".".join(L_proc)


if __name__ == "__main__":
    print ("Assume IMDB is downloaded from https://ai.stanford.edu/~amaas/data/sentiment, and extracted to ../texts/IMDB/aclImdb, where the train/test folders are at ../texts/IMDB/aclImdb/{train, test} directories.")

    preprocess_imdb()