'''
Created on 2014-01-18

@author: Wei
'''
import os
os.environ["PYTHONIOENCODING"] = "utf-8"

import subprocess
import paths
from document.sentence import Sentence
from document.token import Token
from trees.lexicalized_tree import LexicalizedTree
from prep import prep_utils
import os.path
from prep.syntax_parser import SyntaxParser
from document.dependency import Dependency
import re

class Preprocesser:
    def __init__(self):        
        self.syntax_parser = None
        
        try:
            self.syntax_parser = SyntaxParser()
        except Exception as e:
            raise e
        
        self.max_sentence_len = 100
    
    def heuristic_sentence_splitting(self, raw_sent):
        if len(raw_sent) == 0:
            return []
        
        if len(raw_sent.split()) <= self.max_sentence_len:
            return [raw_sent]
  
        i = len(raw_sent) // 2
        j = i
        k = i + 1
        boundaries = [';', ':', '!', '?']
        
        results = []
        while j > 0 and k < len(raw_sent) - 1:
            if raw_sent[j] in boundaries:
                l_sent = raw_sent[ : j + 1]
                r_sent = raw_sent[j + 1 : ].strip()
                
                if len(l_sent.split()) > 1 and len(r_sent.split()) > 1:
                    results.extend(self.heuristic_sentence_splitting(l_sent))
                    results.extend(self.heuristic_sentence_splitting(r_sent))
                    return results
                else:
                    j -= 1
                    k += 1
            elif raw_sent[k] in boundaries:
                l_sent = raw_sent[ : k + 1]
                r_sent = raw_sent[k + 1 : ].strip()
                
                if len(l_sent.split()) > 1 and len(r_sent.split()) > 1:
                    results.extend(self.heuristic_sentence_splitting(l_sent))
                    results.extend(self.heuristic_sentence_splitting(r_sent))
                    return results
                else:
                    j -= 1
                    k += 1
            else:
                j -= 1
                k += 1
        
        if len(results) == 0:
            return [raw_sent]
                

    def parse_single_sentence(self, raw_text):
        return self.syntax_parser.parse_sentence(raw_text)
    
    
    def process_single_sentence(self, doc, raw_text, end_of_para):
        sentence = Sentence(len(doc.sentences), raw_text + (b'<s>' if not end_of_para else b'<P>'), doc)
        
   
        parse_tree_str, deps_str = self.parse_single_sentence(raw_text)
        # self.parse_single_sentence(raw_text) returns different result from 
        # self.syntax_parser.parse_sentence(raw_text)
        
        if type(parse_tree_str) is bytes:
            parse_tree_str = str(parse_tree_str, "utf-8")
        
        if type(deps_str) is bytes:
            deps_str = str(deps_str, "utf-8")

        parse = LexicalizedTree.fromstring(parse_tree_str, leaf_pattern = '(?<=\\s)[^\)\(]+')  
        sentence.set_unlexicalized_tree(parse)
        
        for (token_id, te) in enumerate(parse.leaves()):
            word = te
            token = Token(word, token_id + 1, sentence)
            sentence.add_token(token)

        heads = self.get_heads(sentence, deps_str.split('\n'))
        sentence.heads = heads
        sentence.set_lexicalized_tree(prep_utils.create_lexicalized_tree(parse, heads))
     
        doc.add_sentence(sentence)
    
    def get_heads(self, sentence, dep_elems):
        heads = []
        for token in sentence.tokens:
            heads.append([token.word, token.get_PoS_tag(), 0])
            
        for dep_e in dep_elems:
            m = re.match('(.+?)\((.+?)-(\d+?), (.+?)-(\d+?)\)', dep_e)
            if m:
                relation = m.group(1)
                gov_id = int(m.group(3))
                dep_id = int(m.group(5))

                heads[dep_id - 1][2] = gov_id
                sentence.add_dependency(Dependency(gov_id, dep_id, relation))

        return heads


    def sentence_splitting(self, str_utt, doc, log_writer=None):
        doc.sentences = []
        
        cmd = ["perl", os.path.join(paths.SSPLITTER_PATH,'boundary2.pl'), "-d",os.path.join(paths.SSPLITTER_PATH,'HONORIFICS'), "-i", str_utt ]
        #cmd = 'perl %s -d %s -i %s' % ( os.path.join(paths.SSPLITTER_PATH,'boundary2.pl'), os.path.join(paths.SSPLITTER_PATH, 'HONORIFICS'), str_utt )

        p = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = False)

        #p.wait()
        output, errdata = p.communicate()
        #print(output)
        if len(errdata) == 0:
            
            raw_paras = output.strip().split(b'\n\n')
            seg_sents = []
            for raw_string in raw_paras:
                raw_sentences = raw_string.split(b'\n')
                for (i, raw_sent) in enumerate(raw_sentences):
                    if len(raw_sent.split()) > self.max_sentence_len:
                        chunked_raw_sents = self.heuristic_sentence_splitting(raw_sent)
                        if len(chunked_raw_sents) == 1:
                            continue
                        
                        for (j, sent) in enumerate(chunked_raw_sents):
                            seg_sents.append((sent, i == len(raw_sentences) - 1 and j == len(chunked_raw_sents)))
                    else:
                        seg_sents.append((raw_sent, i == len(raw_sentences) - 1))
        else:
            raise NameError("*** Sentence splitter crashed, with trace %s..." % errdata)
        
        
        print(seg_sents)
        for (i, (raw_text, end_of_para)) in enumerate(seg_sents):
            if i % 10 == 0:
                print ('Processing segment %d out of %d' % (i, len(seg_sents)))
            
            self.process_single_sentence(doc, raw_text, end_of_para)
                

    def preprocess(self, str_utt, doc, log_writer=None):
        self.sentence_splitting(str_utt, doc, log_writer)
        

    def unload(self):
        if self.syntax_parser:
            self.syntax_parser.unload()
