#!/bin/bash

set -e

# Download models
BASE_URL="https://analytics.wikimedia.org/published/wmf-ml-models/mint/20250514081434"
BASE_MODEL_DIR="models"
mkdir -p "$BASE_MODEL_DIR"

download_models() {
	local url="$1"
	local dest_path="$2"

	if [ "${USE_S3CMD:-false}" = true ]; then
		echo "Downloading using s3cmd: $url"
		s3cmd get "$url" "$dest_path"
	else
		echo "Downloading using wget: $url"
		wget --no-verbose --show-progress --progress=bar:force:noscroll "$url" -O "$dest_path"
	fi
}

push_tgz() {
	local tgz_path="$MODEL_TGZ_PATH"
	local target_dir="$MODEL_DIR"

	echo "Extracting $tgz_path into $target_dir"
	mkdir -p "$target_dir"
	tar xvzf "$tgz_path" -C "$target_dir" --strip-components=1
	rm -f "$tgz_path"
}

download_zipped_models() {
	local base_url="$1"
	local model_zip="$2"
	local dest_dir="$3"

	local model_dir="$dest_dir/${model_zip%.zip}"
	local zip_path="$dest_dir/$model_zip"

	if [ -d "$model_dir" ]; then
		echo "$model_zip already extracted, skipping."
	else
		download_models "$base_url/$model_zip" "$zip_path"
		pushd "$dest_dir" > /dev/null
		unzip -o "$model_zip"
		rm -f "$model_zip"
		popd > /dev/null
	fi
}

# The big generic model
MODEL_NAME="nllb200-600M"
MODEL_TGZ="${MODEL_NAME}.tgz"
MODEL_DIR="${BASE_MODEL_DIR}/${MODEL_NAME}"
MODEL_BASE_URL="${BASE_URL}/nllb"
MODEL_URL="${MODEL_BASE_URL}/${MODEL_TGZ}"
MODEL_TGZ_PATH="${BASE_MODEL_DIR}/${MODEL_TGZ}"

download_models "$MODEL_URL" "$MODEL_TGZ_PATH"
push_tgz

# Wikipedia optimized model with limited languages
MODEL_NAME="nllb-wikipedia"
MODEL_TGZ="${MODEL_NAME}.tgz"
MODEL_DIR="${BASE_MODEL_DIR}/${MODEL_NAME}"
MODEL_BASE_URL="${BASE_URL}/nllb"
MODEL_URL="${MODEL_BASE_URL}/${MODEL_TGZ}"
MODEL_TGZ_PATH="${BASE_MODEL_DIR}/${MODEL_TGZ}"

download_models "$MODEL_URL" "$MODEL_TGZ_PATH"
push_tgz

# MADLAD-400 NMT model
MODEL_NAME="madlad400-3b-ct2"
MODEL_TGZ="${MODEL_NAME}.tgz"
MODEL_DIR="${BASE_MODEL_DIR}/${MODEL_NAME}"
MODEL_BASE_URL="${BASE_URL}/madlad400"
MODEL_URL="${MODEL_BASE_URL}/${MODEL_TGZ}"
MODEL_TGZ_PATH="${BASE_MODEL_DIR}/${MODEL_TGZ}"

download_models "$MODEL_URL" "$MODEL_TGZ_PATH"
push_tgz

# Indictrans2 models for English to Indic languages
MODEL_NAME="indictrans-en-indic"
MODEL_TGZ="${MODEL_NAME}.tgz"
MODEL_DIR="${BASE_MODEL_DIR}/${MODEL_NAME}"
MODEL_BASE_URL="${BASE_URL}/indictrans2"
MODEL_URL="${MODEL_BASE_URL}/${MODEL_TGZ}"
MODEL_TGZ_PATH="${BASE_MODEL_DIR}/${MODEL_TGZ}"

download_models "$MODEL_URL" "$MODEL_TGZ_PATH"
push_tgz

# Indictrans2 models for Indic languages to English
MODEL_NAME="indictrans-indic-en"
MODEL_TGZ="${MODEL_NAME}.tgz"
MODEL_DIR="${BASE_MODEL_DIR}/${MODEL_NAME}"
MODEL_BASE_URL="${BASE_URL}/indictrans2"
MODEL_URL="${MODEL_BASE_URL}/${MODEL_TGZ}"
MODEL_TGZ_PATH="${BASE_MODEL_DIR}/${MODEL_TGZ}"

download_models "$MODEL_URL" "$MODEL_TGZ_PATH"
push_tgz

# Indictrans2 models for translating between Indic languages
MODEL_NAME="indictrans2-indic-indic"
MODEL_TGZ="${MODEL_NAME}.tgz"
MODEL_DIR="${BASE_MODEL_DIR}/${MODEL_NAME}"
MODEL_BASE_URL="${BASE_URL}/indictrans2"
MODEL_URL="${MODEL_BASE_URL}/${MODEL_TGZ}"
MODEL_TGZ_PATH="${BASE_MODEL_DIR}/${MODEL_TGZ}"

download_models "$MODEL_URL" "$MODEL_TGZ_PATH"
push_tgz

# OpusMT optimized model with limited languages
MODEL_BASE_URL="${BASE_URL}/opusmt"
for i in opusmt-en-bcl.zip opusmt-en-bi.zip opusmt-en-chr.zip opusmt-en-guw.zip \
         opusmt-en-srn.zip opusmt-en-to.zip opusmt-en-ty.zip opusmt-en-ve.zip \
         opusmt-sv-fi.zip opusmt-fr-ty.zip opusmt-en-fr-br.zip
do
	MODEL_URL="${MODEL_BASE_URL}/${i}"
	download_zipped_models "$MODEL_BASE_URL" "$i" "$BASE_MODEL_DIR"
done

# Softcatala NMT models
MODEL_BASE_URL=${BASE_URL}/softcatala
MODEL_DIR=${BASE_MODEL_DIR}
for i in softcatala-de-ca.zip softcatala-en-ca.zip softcatala-es-ca.zip softcatala-fr-ca.zip softcatala-gl-ca.zip \
         softcatala-ca-de.zip softcatala-ca-en.zip softcatala-ca-es.zip softcatala-ca-fr.zip softcatala-ca-gl.zip \
         softcatala-it-ca.zip softcatala-ja-ca.zip softcatala-nl-ca.zip softcatala-oc-ca.zip softcatala-pt-ca.zip \
         softcatala-ca-it.zip softcatala-ca-ja.zip softcatala-ca-nl.zip softcatala-ca-oc.zip softcatala-ca-pt.zip
do
	MODEL_URL="${MODEL_BASE_URL}/${i}"
	download_zipped_models "$MODEL_BASE_URL" "$i" "$BASE_MODEL_DIR"
done

echo "Starting server..."
# We exec in order to allow gunicorn to handle signals and not have them caught by bash
exec gunicorn "$@"
