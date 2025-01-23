#!/bin/bash

set -e

# Download models
BASE_URL=${BASE_URL:-"https://people.wikimedia.org/~santhosh"}
BASE_MODEL_DIR="models"
mkdir -p $BASE_MODEL_DIR

# The big generic model
MODEL_BASE_URL="${BASE_URL}/nllb/nllb200-600M"
MODEL_DIR="${BASE_MODEL_DIR}/nllb200-600M"
mkdir -p $MODEL_DIR
if [ -d "${MODEL_DIR}" ] && [ "$(ls -A $MODEL_DIR)" ]; then
	echo "Model already exists, skipping download."
else
	echo "Downloading $MODEL_BASE_URL/nllb200-600M.tgz"
	wget -N --no-verbose --show-progress --progress=bar:force:noscroll "${MODEL_BASE_URL}/nllb200-600M.tgz" -P $BASE_MODEL_DIR
	pushd $BASE_MODEL_DIR
	tar xvzf "nllb200-600M.tgz"
	rm -rf "nllb200-600M.tgz"
	popd
fi

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
for i in opusmt-en-bcl.zip opusmt-en-bi.zip opusmt-en-chr.zip opusmt-en-guw.zip \
         opusmt-en-srn.zip opusmt-en-to.zip opusmt-en-ty.zip opusmt-en-ve.zip \
         opusmt-sv-fi.zip opusmt-fr-ty.zip opusmt-en-fr-br.zip
do
	if [ -d "${MODEL_DIR}/${i%.zip}" ]; then
		continue
	else
		echo "Downloading $MODEL_BASE_URL/${i}"
		wget -N --no-verbose --show-progress --progress=bar:force:noscroll "${MODEL_BASE_URL}"/"${i}" -P $MODEL_DIR
		# Extract the OpusMT optimized model
		pushd $BASE_MODEL_DIR
		unzip "${i}"
		rm -rf "${i}"
		popd
	fi
done

# Softcatala NMT models
MODEL_BASE_URL=${BASE_URL}/softcatala
MODEL_DIR=${BASE_MODEL_DIR}
for i in softcatala-de-ca.zip softcatala-en-ca.zip softcatala-es-ca.zip softcatala-fr-ca.zip softcatala-gl-ca.zip \
         softcatala-ca-de.zip softcatala-ca-en.zip softcatala-ca-es.zip softcatala-ca-fr.zip softcatala-ca-gl.zip \
         softcatala-it-ca.zip softcatala-ja-ca.zip softcatala-nl-ca.zip softcatala-oc-ca.zip softcatala-pt-ca.zip \
         softcatala-ca-it.zip softcatala-ca-ja.zip softcatala-ca-nl.zip softcatala-ca-oc.zip softcatala-ca-pt.zip
do
	if [ -d "${MODEL_DIR}/${i%.zip}" ]; then
		continue
	else
		echo "Downloading $MODEL_BASE_URL/${i}"
		wget -N --no-verbose --show-progress --progress=bar:force:noscroll "${MODEL_BASE_URL}"/"${i}" -P $MODEL_DIR
		# Extract the Softcatala optimized model
		pushd $BASE_MODEL_DIR
		unzip "${i}"
		rm -rf "${i}"
		popd
	fi
done

# MADLAD-400 NMT model
MODEL_BASE_URL="${BASE_URL}/madlad400-3b-ct2"
MODEL_DIR="${BASE_MODEL_DIR}/madlad400-3b-ct2"
mkdir -p $MODEL_DIR
if [ -d "${MODEL_DIR}" ] && [ "$(ls -A $MODEL_DIR)" ]; then
	echo "Model already exists, skipping download."
else
	echo "Downloading $MODEL_BASE_URL/madlad400-3b-ct2.tgz"
	wget -N --no-verbose --show-progress --progress=bar:force:noscroll "${MODEL_BASE_URL}/madlad400-3b-ct2.tgz" -P $BASE_MODEL_DIR
	pushd $BASE_MODEL_DIR
	tar xvzf "madlad400-3b-ct2.tgz"
	rm -rf "madlad400-3b-ct2.tgz"
	popd
fi

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

# Indictrans2 models for translating between Indic languages
MODEL_BASE_URL="${BASE_URL}/indictrans2/indictrans2-indic-indic"
MODEL_DIR="${BASE_MODEL_DIR}/indictrans2-indic-indic"
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
