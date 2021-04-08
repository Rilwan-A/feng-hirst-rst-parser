import os.path
import inspect

if "rl_conv" in os.getcwd():
    ROOT_PATH = "/home/u1862646/01_Mcv/mastering-conversation/rl_conv/pretrain/DockerImages/feng_hirst_rst_parser/"
    #curr_fp = inspect.getsourcefile()
    curr_fp = os.path.abspath(__file__)
    ROOT_PATH = os.path.dirname( os.path.dirname( curr_fp ) )
else:
    ROOT_PATH = '/'.join(os.path.split(os.getcwd())[ : -1])


PARSED_TEXTS_PATH = os.path.join(ROOT_PATH, 'texts/parsed_texts/')
STANFORD_PATH = os.path.join(ROOT_PATH, 'tools/stanford_parser/')
PENN2MALT_PATH = os.path.join(ROOT_PATH, 'tools/Penn2Malt/')
SVM_TOOLS = os.path.join(ROOT_PATH, 'tools/svm_tools/')
CRFSUITE_PATH = os.path.abspath( os.path.join(ROOT_PATH, 'tools/crfsuite/') )
MALLET_PATH = os.path.join(ROOT_PATH, 'tools/mallet-2.07/')
STANFORD_CORENLP_PATH = os.path.join(ROOT_PATH, 'tools/stanford-corenlp-full-2013-11-12/')
CHARNIAK_PARSER_PATH = '/u/weifeng/Projects/CRF_segmenter/tools/CharniakParserRerank/'
SSPLITTER_PATH = os.path.abspath( os.path.join(ROOT_PATH, 'tools/CCGSsplitter/') )
STANFORD_PARSER_PATH = os.path.join(ROOT_PATH, 'tools/stanford-parser-full-2014-01-04/')

MODEL_PATH = os.path.join(ROOT_PATH, 'model/')
TREE_BUILD_MODEL_PATH = os.path.join(MODEL_PATH, 'tree_build_set_CRF/')
SEGMENTER_MODEL_PATH = os.path.join(MODEL_PATH, 'seg_set_CRF/')
#CHARNIAK_PARSER_MODEL_PATH = os.path.join(MODEL_PATH, 'WSJ+Gigaword/')
CHARNIAK_PARSER_MODEL_PATH = os.path.join(MODEL_PATH, 'WSJ/')
SBD_MODEL_PATH = os.path.join(MODEL_PATH, 'sbd_models/model_nb/')

tmp_folder = os.path.join(ROOT_PATH, 'tmp/')

save_folder = os.path.join(MODEL_PATH, 'serial_data/')

RST_DT_ROOT = os.path.join(ROOT_PATH, 'texts/RST_DT_fixed/')
OUTPUT_PATH = os.path.join(ROOT_PATH, 'texts/results/')
DECOREF_PATH = os.path.join(ROOT_PATH, 'texts/dcoref/')

LOGS_PATH = os.path.join(ROOT_PATH, 'logs/')
