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


def main(li_utterances,
            verbose=False,
            skip_parsing=False,
            global_features=True,
            logging=False,
            redirect_output=False):
    """[summary]

    Args:
        li_utterances ([type]): [json encoded li-utteranc]

    Returns:
        [type]: [description]
    """
    parser_stdout_filepath = 'parser.stdout'
    li_utterances = json.loads(li_utterances)
    kwargs = {
        'verbose':verbose,
        'skip_parsing':skip_parsing,
        'global_features':global_features,
        'logging':logging
    }
    # if len(args) != 1:
    #     sys.stderr.write("Please provide (only) one file to parse.")
    #     sys.exit(1)

    # output_filepath = get_output_filepath(args)

    # if os.path.isfile(output_filepath):
    #     # You can't parse a file with the same name twice, unless you
    #     # remove the parser output file first.
    #     os.remove(output_filepath)

    # re-route the print/stdout output of the parser to a file
    if redirect_output:
        old_stdout = sys.stdout
        sys.stdout = open(parser_stdout_filepath, "w", buffering=1)
    try:
        results = feng_main(li_utterances, **kwargs) #li of parse trees

        assert len(results) != 0

    except AssertionError as e:
        e.args += ("Expected parse trees as a result, but got: {0}.\n"
             "Parser STDOUT was:\n{1}").format(
                results, get_parser_stdout(parser_stdout_filepath))
        raise e

    finally:
        if redirect_output:
            sys.stdout.close()
            sys.stdout = old_stdout
        pass

    #parse_tree = results[0].__repr__() + "\n"

    # sys.stdout.write(parse_tree)
    # sys.stdout.write(str(type(results[0])) ) 
    # sys.stdout.write(str(type(results)))
    # sys.stdout.write(str( results[0].__class__.__module__))


    escaped_parse_trees = json.dumps([pt.pformat(parens='{}' ) for pt in results])
    #return results
    sys.stdout.write(escaped_parse_trees)
    return escaped_parse_trees


if __name__ == "__main__":
    parser = argparse.ArgumentParser( )
    parser.add_argument('--li_utterances',type=str, 
        default=json.dumps( ["Shut up janice, you've always been a hater","If you're here then how can you be there too"]),
        )
    
    parser.add_argument('--skip-parsing',type=bool, default=False)
    parser.add_argument('--global_features',type=bool,default=True)
    parser.add_argument('--logging',type=bool, default=False)
    parser.add_argument('--redirect_output',type=bool,default=True)

    args = parser.parse_args()
    
    main( **vars(args) )
