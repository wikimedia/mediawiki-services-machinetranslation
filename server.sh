#!/bin/bash

# Download models
mkdir -p models

# The big generic model
# wget -N https://translate.wmcloud.org/static/nllb200/nllb200-600M/config.json -P models/nllb200-600M
# wget -N https://translate.wmcloud.org/static/nllb200/nllb200-600M/model.bin  -P models/nllb200-600M
# wget -N https://translate.wmcloud.org/static/nllb200/nllb200-600M/sentencepiece.bpe.model -P models/nllb200-600M
# wget -N https://translate.wmcloud.org/static/nllb200/nllb200-600M/shared_vocabulary.txt -P models/nllb200-600M


wget -N https://translate.wmcloud.org/static/nllb200/nllb-wikipedia/config.json -P models/nllb-wikipedia
wget -N https://translate.wmcloud.org/static/nllb200/nllb-wikipedia/model.bin  -P models/nllb-wikipedia
wget -N https://translate.wmcloud.org/static/nllb200/nllb-wikipedia/sentencepiece.bpe.model -P models/nllb-wikipedia
wget -N https://translate.wmcloud.org/static/nllb200/nllb-wikipedia/shared_vocabulary.txt -P models/nllb-wikipedia

gunicorn
