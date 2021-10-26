# -*- coding: utf-8 -*-

import os
import subprocess
import paths
import os.path
import io


class CRFClassifier:
    def __init__(self, name, model_type, model_path, model_file, verbose):
        self.verbose = verbose
        self.name = name
        self.type = model_type
        self.model_fname = model_file
        self.model_path = model_path

        if not os.path.exists(os.path.join(self.model_path, self.model_fname)):
            print('The model path %s for CRF classifier %s does not exist.' %
                  (os.path.join(self.model_path, self.model_fname), name))
            raise OSError('Could not create classifier subprocess')

        self.classifier_cmd = ["{}/crfsuite-stdin".format(paths.CRFSUITE_PATH), "tag", "-pi", "-m",
                               os.path.join(self.model_path, self.model_fname), "-"]

        self.classifier = subprocess.Popen(self.classifier_cmd, shell=False, stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=io.DEFAULT_BUFFER_SIZE*5,
                                           )

        if self.classifier.poll():
            raise OSError('Could not create classifier subprocess, with error info:\n%s' %
                          self.classifier.stderr.readline())

        #self.cnt = 0

    def classify(self, vectors):
        """
            Parameters
            ----------
            vectors : list of str
                list of features, e.g. 'LEAF\tNum_EDUs=1\r'

            Returns
            -------
            seq_prob : float
                sequence probability
            predictions : list of (str, float) tuples
                list of predition tuples (label, probability)
        """
        try:
            _ = '\n'.join(vectors) + "\n\n"
            _ = _.encode('utf-8')
            self.classifier.stdin.write(_)
            
        except TypeError as e:

            _ = '\n'.join(vectors) + "\n\n"
            self.classifier.stdin.write(_)

            # self.classifier.stdin.flush()

        try:
            self.classifier.stdin.close()
        except IOError as e:
            raise Exception(str(e) + " \n  string: {}".format(
                [l.decode('utf-8') for l in self.classifier.stdout.readlines()]))

        lines = [l.decode('ascii') for l in self.classifier.stdout.readlines()]

        if self.classifier.poll():
            raise OSError('crf_classifier subprocess died')

        predictions = []

        for line in lines[1:]:
            line = line.strip()
            if line != '':
                fields = line.split(':')
                label = fields[0]
                prob = float(fields[1])
                predictions.append((label, prob))

        seq_prob = float(lines[0].split('\t')[1])

        # re-create classifier (because we had to close STDIN earlier)
        self.classifier = subprocess.Popen(self.classifier_cmd, shell=False, stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=io.DEFAULT_BUFFER_SIZE*4)

        return seq_prob, predictions

    def poll(self):
        """
        Checks that the classifier processes are still alive
        """
        if self.classifier is None:
            return True
        else:
            return self.classifier.poll() != None

    def unload(self):
        if self.classifier and not self.poll():
            self.classifier.stdin.write(b'\n')
            print('Successfully unloaded %s' % self.name)
            self.classifier.kill()
            # self.classifier.kill()
            # del self.classifier
