#!/bin/bash

# Download models
mkdir -p models

echo "Downloading models..."

# The big generic model
modelbase=https://people.wikimedia.org/~santhosh/nllb/nllb200-600M
wget -N --no-verbose --show-progress --progress=bar:force:noscroll $modelbase/config.json -P models/nllb200-600M
wget -N --no-verbose --show-progress --progress=bar:force:noscroll $modelbase/model.bin -P models/nllb200-600M
wget -N --no-verbose --show-progress --progress=bar:force:noscroll $modelbase/sentencepiece.bpe.model -P models/nllb200-600M
wget -N --no-verbose --show-progress --progress=bar:force:noscroll $modelbase/shared_vocabulary.txt -P models/nllb200-600M


# Wikipedia optimized model with limited languages
wikimodelbase=https://people.wikimedia.org/~santhosh/nllb/nllb-wikipedia
wget -N --no-verbose --show-progress --progress=bar:force:noscroll $wikimodelbase/config.json -P models/nllb-wikipedia
wget -N --no-verbose --show-progress --progress=bar:force:noscroll $wikimodelbase/model.bin -P models/nllb-wikipedia
wget -N --no-verbose --show-progress --progress=bar:force:noscroll $wikimodelbase/sentencepiece.bpe.model -P models/nllb-wikipedia
wget -N --no-verbose --show-progress --progress=bar:force:noscroll $wikimodelbase/shared_vocabulary.txt -P models/nllb-wikipedia

# OpusMT optimized model with limited languages
wikimodelbase=https://people.wikimedia.org/~santhosh/opusmt
wget -N --no-verbose --show-progress --progress=bar:force:noscroll $wikimodelbase/opusmt-en-bcl.zip -P models
cd models
unzip opusmt-en-bcl.zip
rm -rf opusmt-en-bcl.zip
cd ..

echo "Models downloaded. Starting server..."

gunicorn
