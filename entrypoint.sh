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
for i in opusmt-en-bcl.zip opusmt-en-to.zip opusmt-en-chr.zip
do
	if [ -d "${MODEL_DIR}/${i%.zip}" ]; then
		continue
	else
		echo "Downloading $MODEL_BASE_URL/${i}"
		wget -N --no-verbose --show-progress --progress=bar:force:noscroll "${MODEL_BASE_URL}"/${i} -P $MODEL_DIR
		# Extract the OpusMT optimized model
		pushd $BASE_MODEL_DIR
		unzip ${i}
		rm -rf ${i}
		popd
	fi
done

# Softcatala NMT model for English to Catalan
MODEL_BASE_URL=${BASE_URL}/softcatala
MODEL_DIR=${BASE_MODEL_DIR}
for i in softcatala-en-ca.zip
do
	if [ -d "${MODEL_DIR}/${i%.zip}" ]; then
		continue
	else
		echo "Downloading $MODEL_BASE_URL/${i}"
		wget -N --no-verbose --show-progress --progress=bar:force:noscroll "${MODEL_BASE_URL}"/${i} -P $MODEL_DIR
		# Extract the Softcatala optimized model
		pushd $BASE_MODEL_DIR
		unzip softcatala-en-ca.zip
		rm -rf softcatala-en-ca.zip
		popd
	fi
done



# Indictrans2 models for Indic languages to English
MODEL_BASE_URL="${BASE_URL}/indictrans2/indictrans-indic-en"
MODEL_DIR="${BASE_MODEL_DIR}/indictrans2-indic-en"
for i in config.json model.bin model.SRC source_vocabulary.txt target_vocabulary.txt
do
	if [ -f "${MODEL_DIR}/${i}" ]; then
		continue
	else
		echo "Downloading $MODEL_BASE_URL/${i}"
		wget -N --no-verbose --show-progress --progress=bar:force:noscroll "${MODEL_BASE_URL}"/${i} -P $MODEL_DIR
	fi
done

# Indictrans2 models for English to Indic languages
MODEL_BASE_URL="${BASE_URL}/indictrans2/indictrans-en-indic"
MODEL_DIR="${BASE_MODEL_DIR}/indictrans2-en-indic"
for i in config.json model.bin model.SRC source_vocabulary.txt target_vocabulary.txt
do
	if [ -f "${MODEL_DIR}/${i}" ]; then
		continue
	else
		echo "Downloading $MODEL_BASE_URL/${i}"
		wget -N --no-verbose --show-progress --progress=bar:force:noscroll "${MODEL_BASE_URL}"/${i} -P $MODEL_DIR
	fi
done


echo "Starting server..."
# We exec in order to allow gunicorn to handle signals and not have them caught by bash
exec gunicorn "$@"
