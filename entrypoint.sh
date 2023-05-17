#!/bin/bash

set -e

# Download models
BASE_URL=${BASE_URL:-"https://people.wikimedia.org/~santhosh"}
BASE_MODEL_DIR="models"
mkdir -p $BASE_MODEL_DIR

# The big generic model
MODEL_BASE_URL="${BASE_URL}/nllb/nllb200-600M"
MODEL_DIR="${BASE_MODEL_DIR}/nllb200-600M"
for i in config.json model.bin sentencepiece.bpe.model shared_vocabulary.txt
do
	if [ -f "${MODEL_DIR}/${i}" ]; then
		continue
	else
		echo "Downloading $MODEL_BASE_URL/${i}"
		wget -N --no-verbose --show-progress --progress=bar:force:noscroll "${MODEL_BASE_URL}"/${i} -P $MODEL_DIR
	fi
done

# Wikipedia optimized model with limited languages
MODEL_BASE_URL="${BASE_URL}/nllb/nllb-wikipedia"
MODEL_DIR="${BASE_MODEL_DIR}/nllb-wikipedia"
for i in config.json model.bin sentencepiece.bpe.model shared_vocabulary.txt
do
	if [ -f "${MODEL_DIR}/${i}" ]; then
		continue
	else
		echo "Downloading $MODEL_BASE_URL/${i}"
		wget -N --no-verbose --show-progress --progress=bar:force:noscroll "${MODEL_BASE_URL}"/${i} -P $MODEL_DIR
	fi
done

# OpusMT optimized model with limited languages
MODEL_BASE_URL=${BASE_URL}/opusmt
MODEL_DIR=${BASE_MODEL_DIR}
for i in opusmt-en-bcl.zip
do
	if [ -d "${MODEL_DIR}/${i%.zip}" ]; then
		continue
	else
		echo "Downloading $MODEL_BASE_URL/${i}"
		wget -N --no-verbose --show-progress --progress=bar:force:noscroll "${MODEL_BASE_URL}"/${i} -P $MODEL_DIR
		# Extract the OpusMT optimized model
		pushd $BASE_MODEL_DIR
		unzip opusmt-en-bcl.zip
		rm -rf opusmt-en-bcl.zip
		popd
	fi
done

echo "Starting server..."
# We exec in order to allow gunicorn to handle signals and not have them caught by bash
exec gunicorn "$@"
