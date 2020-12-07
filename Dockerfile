FROM alpine:3.9 as builder

RUN apk update && \
    apk add git py2-setuptools py2-pip build-base openjdk8-jre perl && \
    apk add bash && \
    pip install nltk==3.4 pytest argparse

WORKDIR /opt

#TODO: Uncomment below for replicable version
#RUN git clone https://github.com/Akanni96/feng-hirst-rst-parser.git
RUN mkdir feng-hirst-rst-parser
ADD . /opt/feng-hirst-rst-parser

# The Feng's original README claims that liblbfgs is included, but it's not
WORKDIR /opt/feng-hirst-rst-parser/tools/crfsuite
RUN wget https://github.com/downloads/chokkan/liblbfgs/liblbfgs-1.10.tar.gz && \
    tar xfvz liblbfgs-1.10.tar.gz && \
    rm liblbfgs-1.10.tar.gz

# TO-DO add this to docker file setup
WORKDIR /opt/feng-hirst-rst-parser/tools/crfsuite/liblbfgs-1.10
RUN ./configure --prefix=$HOME/local && \
    make && \
    make install

WORKDIR /opt/feng-hirst-rst-parser/tools/crfsuite/crfsuite-0.12
# Can't put chmod and ./configure in the same layer (to avoid "is busy" error)
RUN chmod +x configure install-sh
RUN ./configure --prefix=$HOME/local --with-liblbfgs=$HOME/local && \
    make && \
    make install && \
    cp /root/local/bin/crfsuite /opt/feng-hirst-rst-parser/tools/crfsuite/crfsuite-stdin && \
    chmod +x /opt/feng-hirst-rst-parser/tools/crfsuite/crfsuite-stdin


FROM alpine:3.9

RUN apk update && \
    apk add py2-pip openjdk8-jre-base perl && \
    apk add bash && \
    pip install nltk==3.4 pytest

WORKDIR /opt/feng-hirst-rst-parser
COPY --from=builder /opt/feng-hirst-rst-parser .

WORKDIR /root/local
COPY --from=builder /root/local .

WORKDIR /opt/feng-hirst-rst-parser/src


#ENTRYPOINT ["/bin/bash"]

# CMD ["parser_wrapper2.py",\
#     "-li_utterance",\
#     '["Shut up janice, you\'ve always been a hater", "If you\'re here then how can you be there too"]']

ENTRYPOINT ["/opt/feng-hirst-rst-parser/src/parser_wrapper2.py"]
CMD ["--li_utterance", '["Shut up janice, you\'ve always been a hater", "If you\'re here then how can you be there too"]']

#CMD ["../texts/input_long.txt"]
