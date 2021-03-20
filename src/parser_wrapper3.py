#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os

import sys
# reload(sys)
# sys.setdefaultencoding("utf-8")

"""
Simple wrapper around the Feng-Hirst parser, used as an entry point for
a Docker container.

In contrast to parse.py, this script only accepts one input file.
Since parse.py is quite chatty, it's stdout will be suppressed and stored
in a file. If the parser doesn't produce a parse, this file will
be printed to stderr.

In contrast to parser_wrapper.py, this script accepts a list of input files.
Since parse.py is quite chatty, it's stdout will be supressed and stored in a file.
If the parer doesn't return a list of parses, a json of the list will be printed to stderr
"""

from nltk.tree import ParentedTree
#from parse2 import parse_args
from parse2 import main as feng_main
import argparse
import json

class ParserException(Exception):
    pass

def get_parser_stdout(parser_stdout_filepath):
    """Returns the re-routed STDOUT of the Feng/Hirst parser."""
    sys.stdout.close()
    stdout_file = open(parser_stdout_filepath)
    stdout_str = stdout_file.read()
    stdout_file.close()
    sys.stdout = open(parser_stdout_filepath, "w")
    return stdout_str

# def get_output_filepath(args):
#     """Returns the path to the output file of the parser."""
#     input_filepath = args[0]
#     input_filename = os.path.basename(input_filepath)
#     return os.path.join("../texts/results", "{}.tree".format(input_filename))


def main(json_li_li_utterances,
            verbose=False,
            skip_parsing=False,
            global_features=True,
            logging=False,
            redirect_output=0):
    """[summary]

    Args:
        li_utterances ([type]): [json encoded li_utterances]

    Returns:
        [type]: [description]
    """
    parser_stdout_filepath = 'parser.stdout'
    li_li_utterances = json.loads(json_li_li_utterances)
    kwargs = {
        'verbose':verbose,
        'skip_parsing':skip_parsing,
        'global_features':global_features,
        'logging':logging
    }

    li_li_segtext = []
    li_li_parse_trees= []
    for li_utterances in li_li_utterances:
    # re-route the print/stdout output of the parser to a file
        if redirect_output in [0,1]:
            old_stdout = sys.stdout
            sys.stdout = open(parser_stdout_filepath, "w", buffering=1)

        elif redirect_output in [2,3]:
            old_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w', buffering=1)
            
        try:
            results = feng_main(li_utterances, **kwargs) #li of parse trees

            assert len(results) != 0

        except AssertionError as e:
            e.args += ("Expected parse trees as a result, but got: {0}.\n"
                "Parser STDOUT was:\n{1}").format(
                    results, get_parser_stdout(parser_stdout_filepath))
            results = ''

        finally:
            if redirect_output in [1,2,3]:
                sys.stdout.close()
                sys.stdout = old_stdout                
            pass
            
        if skip_parsing:
            li_segtext= results
            #escaped_li_segtext = json.dumps(li_segtext)            
            li_li_segtext.append( li_segtext )


        else:
            li_parse_trees = [pt.pformat(parens='{}' ) for pt in results]
            li_li_parse_trees.append(li_parse_trees)


    if redirect_output in [0,1,2]:
        if skip_parsing:
            output = json.dumps(li_li_segtext) 
        else:
            output = json.dumps(li_li_parse_trees)
        
        sys.stdout.write(output)
        return None
    
    else:
        if skip_parsing:
            output = li_li_segtext
        else:
            output = li_li_parse_trees
        
        sys.stdout.write(output)
        return None

        


if __name__ == "__main__":
    parser = argparse.ArgumentParser( )
    parser.add_argument('--json_li_li_utterances',type=str, 
        default=json.dumps( [["Shut up janice, you've always been a hater","If you're here then how can you be there too"],
            ["Shut up janice, you've always been a hater","If you're here then how can you be there too"] ]) )
    
    parser.add_argument('--skip_parsing',type=lambda x: bool(int(x)), default=False)
    parser.add_argument('--global_features',type=lambda x: bool(int(x)),default=True)
    parser.add_argument('--logging',type=lambda x: bool(int(x)), default=False)
    parser.add_argument('--redirect_output',type=int, default=0,
                            help="""Mode 0: All output goes to stdout 
                                \n Mode 1: Redirect intemediary outputs to a file. Final output goes to stdout 
                                \n Mode 2: Redirect intemediary output to os.devnull. Returns output to stdout 
                                \n Mode 3: Redirect intemediary and final output to os.devnull. Returns output as python object""")
    #parser.add_argument('--redirect_output',type=lambda x: bool(int(x)),default=True) 

    args = parser.parse_args()
    
    main( **vars(args) )

