#!/bin/bash

# Download models
mkdir -p models

# The big generic model
wget -N https://people.wikimedia.org/~santhosh/nllb/nllb200-600M/config.json -P models/nllb200-600M
wget -N https://people.wikimedia.org/~santhosh/nllb/nllb200-600M/model.bin -P models/nllb200-600M
wget -N https://people.wikimedia.org/~santhosh/nllb/nllb200-600M/sentencepiece.bpe.model -P models/nllb200-600M
wget -N https://people.wikimedia.org/~santhosh/nllb/nllb200-600M/shared_vocabulary.txt -P models/nllb200-600M


# Wikipedia optimized model with limited languages
wget -N https://people.wikimedia.org/~santhosh/nllb/nllb-wikipedia/config.json -P models/nllb-wikipedia
wget -N https://people.wikimedia.org/~santhosh/nllb/nllb-wikipedia/model.bin s-P models/nllb-wikipedia
wget -N https://people.wikimedia.org/~santhosh/nllb/nllb-wikipedia/sentencepiece.bpe.model -P models/nllb-wikipedia
wget -N https://people.wikimedia.org/~santhosh/nllb/nllb-wikipedia/shared_vocabulary.txt -P models/nllb-wikipedia

gunicorn
