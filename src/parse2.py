'''
Created on 2014-01-17

@author: Vanessa Wei Feng
'''
import os

from segmenters.crf_segmenter import CRFSegmenter
from treebuilder.build_tree_CRF import CRFTreeBuilder

from optparse import OptionParser
import argparse
from copy import deepcopy
import paths
import os.path
import re
import sys
from document.doc import Document
import time
import traceback
from datetime import datetime

from logs.log_writer import LogWriter
from prep.preprocesser2 import Preprocesser

import utils.serialize
import utils.rst_lib
import contextlib


PARA_END_RE = re.compile(r' (<P>|<s>)$')


class DiscourseParser():
    def __init__(self, verbose,
                 skip_parsing,
                 global_features,
                 output_dir=None,
                 log_writer=None,
                 segment_and_parse_tree=False):
        self.verbose = verbose
        self.segment_and_parse_tree = segment_and_parse_tree
        if self.segment_and_parse_tree:
            self.skip_parsing = False
        else:
            self.skip_parsing = skip_parsing
        self.global_features = global_features
        self.save_preprocessed_doc = False

        # self.output_dir = os.path.join(paths.OUTPUT_PATH, output_dir if output_dir is not None else '')
        # if not os.path.exists(self.output_dir):
        #     print ('Output directory %s not exists, creating it now.' % self.output_dir)
        #     os.makedirs(self.output_dir)

        self.log_writer = LogWriter(log_writer)
        self.log_writer.write("===========")

        self.feature_sets = 'gCRF'

        # initStart = time.time()

        self.preprocesser = None
        try:
            self.preprocesser = Preprocesser()
        except Exception as e:
            print("*** Loading Preprocessing module failed...")
            print(traceback.print_exc())

            raise e
        try:
            self.segmenter = CRFSegmenter(
                _name=self.feature_sets, verbose=self.verbose, global_features=self.global_features)
        except Exception as e:
            print("*** Loading Segmentation module failed...")
            print(traceback.print_exc())

            raise e

        try:
            if not self.skip_parsing:
                self.treebuilder = CRFTreeBuilder(
                    _name=self.feature_sets, verbose=self.verbose)
            else:
                self.treebuilder = None
        except Exception as e:
            print("*** Loading Tree-building module failed...")
            print(traceback.print_exc())
            raise e

        # initEnd = time.time()
        # print ('Finished initialization in %.2f seconds.\n' % (initEnd - initStart))

    def unload(self):
        if self.preprocesser is not None:
            self.preprocesser.unload()

        if not self.segmenter is None:
            self.segmenter.unload()

        if not self.treebuilder is None:
            self.treebuilder.unload()

    def parse(self, utterance):
        result = None

        try:
            preprocessStart = time.time()
            doc = Document()
            doc.preprocess(utterance, self.preprocesser, self.log_writer)

            preprocessEnd = time.time()

            print('Finished preprocessing in %.2f seconds.' %
                  (preprocessEnd - preprocessStart))
            self.log_writer.write('Finished preprocessing in %.2f seconds.' % (
                preprocessEnd - preprocessStart))

            print('')
        except Exception as e:
            print("*** Preprocessing failed ***")
            print(traceback.print_exc())

            raise e

        try:
            if not doc.segmented:
                segStart = time.time()

                self.segmenter.segment(doc)

                if self.verbose:
                    print('edus')
                    for e in doc.edus:
                        print(e)
                    print(' ')
                    print('cuts')
                    for cut in doc.cuts:
                        print(cut)
                    print(' ')
                    print('edu_word_segmentation')

                segEnd = time.time()
                print('Finished segmentation in %.2f seconds.' %
                      (segEnd - segStart))
                print('Segmented into %d EDUs.' % len(doc.edus))

                self.log_writer.write('Finished segmentation in %.2f seconds. Segmented into %d EDUs.' % (
                    (segEnd - segStart), len(doc.edus)))

            else:
                print('Already segmented into %d EDUs.' % len(doc.edus))

            print(' ')

            if self.verbose:
                for e in doc.edus:
                    print(e)

        except Exception as e:
            print("*** Segmentation failed ***")
            print(traceback.print_exc())

            raise e
            
        try:
            ''' Step 2: build text-level discourse tree '''
            if self.segment_and_parse_tree:
                segmented = self.segment_from_doc(doc)
                parsed_tree = self.parse_tree_from_doc(doc)
                output = (segmented, parsed_tree)
                
            elif self.skip_parsing:
                
                output = self.segment_from_doc(doc)

            else:
                output = self.parse_tree_from_doc(doc)

        except Exception as e:
            if self.verbose:
                print(traceback.print_exc())
            raise e

        print('===================================================')

        return output

    def parse_li_utterances(self, li_utterance):
        results = []

        with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):

            for (i, utt) in enumerate(li_utterance):

                try:
                    result = self.parse(utt)
                    results.append(result)

                except Exception as e:
                    results.append(None)
                    pass
            
            if self.segment_and_parse_tree:
            
                try:
                    segmented_texts, parsed_trees = zip(*[ [res[0], res[1]] if res!=None else [None, None] for res in results ] )
                except Exception as e:
                    pass
                
                parsed_trees = [pt.pformat(
                    parens='{}') if pt != None else None for pt in parsed_trees]
                output = (segmented_texts, parsed_trees)
                
            elif self.skip_parsing:
                output = results

            else:
                li_parse_trees = [pt.pformat(
                    parens='{}') if pt != None else None for pt in results]
                output = li_parse_trees


        return output

    def parse_tree_from_doc(self, doc):

        treeBuildStart = time.time()

        #outfname = os.path.join(self.output_dir, core_filename + ".tree")

        pt = self.treebuilder.build_tree(doc)

        print('Finished tree building.')

        if pt is None:
            print("No tree could be built...")

            if not self.treebuilder is None:
                self.treebuilder.unload()

            return -1

        # Unescape the parse tree
        if pt:
            doc.discourse_tree = pt
            result = deepcopy(pt)
            treeBuildEnd = time.time()

            print('Finished tree building in %.2f seconds.' %
                    (treeBuildEnd - treeBuildStart))
            self.log_writer.write('Finished tree building in %.2f seconds.' % (
                treeBuildEnd - treeBuildStart))

            for i in range(len(doc.edus)):

                # Converting each edu to a string
                for j in range(len(doc.edus[i])):
                    if type(doc.edus[i][j]) != str:
                        doc.edus[i][j] = str(doc.edus[i][j], "utf-8")

                edu_str = ' '.join(doc.edus[i])

                # parse tree with escape symbols
                pt.__setitem__(pt.leaf_treeposition(i),
                                '_!%s!_' % edu_str)

                result.__setitem__(pt.leaf_treeposition(i), PARA_END_RE.sub(
                    '', edu_str))  # parse tree without escape symbols

            #out = pt.pformat()
            #print ('Output tree building result ')

            # f_o = open(outfname, "w")
            # f_o.write(out)
            # f_o.close()
            output = pt
            
        return output

    def segment_from_doc(self,doc):
        text_out = []
        for sentence in doc.sentences:
            sent_id = sentence.sent_id
            edu_segmentation = doc.edu_word_segmentation[sent_id]
            i = 0

            for (j, token) in enumerate(sentence.tokens):
                text_out.append(token.word)
                if j < len(sentence.tokens) - 1 and j == edu_segmentation[i][1] - 1:
                    text_out.append('EDU_BREAK')
                    i += 1
            text_out.append('EDU_BREAK')

            #f_o.write(' '.join(sent_out) + '\n')

        output = text_out
        return output
        
        
def main(li_utterances,
         verbose=False,
         skip_parsing=False,
         global_features=False,
         logging=True):
    parser = None
    results = []

    try:

        output_dir = None
        start_arg = 0

        log_writer = None
        if logging:
            if not os.path.exists(paths.LOGS_PATH):
                os.makedirs(paths.LOGS_PATH)
            log_fname = os.path.join(paths.LOGS_PATH, 'log_%s.txt' % (
                output_dir if output_dir else datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))).replace("\\", "/")
            log_writer = open(log_fname, 'w')

        if logging:
            log_writer.write("00000000000")

        parser = DiscourseParser(verbose, skip_parsing,
                                 global_features,
                                 #output_dir = output_dir,
                                 log_writer=log_writer)

        files = []
        skips = 0

        utt_count = len(li_utterances)
        print('Processing %s utterances' % str(utt_count))

        for (i, utt) in enumerate(li_utterances):
            print('Parsing utterance %d out of %d)' % (i, utt_count))

            try:
                result = parser.parse(utt)
                results.append(result)
                if logging:
                    parser.log_writer.write(
                        '===================================================')

            except Exception as e:
                results.append(None)
                print('Some error occurred, when parsing utterance %d' % i)
                pass

        parser.unload()
        return results

    except Exception as e:
        if not parser is None:
            parser.unload()
        print(str(e))
        raise Exception(traceback.print_exc())


def parse_args():
    usage = "Usage: %prog [options] input_file/dir"

    parser = argparse.ArgumentParser(help=usage)
    parser.add_argument("-v", "--verbose",
                        action="store_true", dest="verbose", default=False,
                        help="verbose mode")
    parser.add_argument("-s", "--skip_parsing",
                        action="store_true", dest="skip_parsing", default=False,
                        help="Skip parsing, i.e., conduct segmentation only.")

    parser.add_argument("-g", "--global_features",
                        action="store_true", dest="global_features", default=True,
                        help="Perform a second pass of EDU segmentation using global features.")
    parser.add_argument("-l", "--logging",
                        action="store_true", dest="logging", default=False,
                        help="Perform logging while parsing.")

    args = argparse.parse_args()

    return args


v = '1.0'
if __name__ == '__main__':
    options, args = parse_args()
    main(options, args)
