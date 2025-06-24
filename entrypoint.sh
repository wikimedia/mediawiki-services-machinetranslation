#!/bin/bash

set -e

BASE_URL="${BASE_URL:-https://analytics.wikimedia.org/published/wmf-ml-models/mint/20250514081434}"
BASE_MODEL_DIR="models"
mkdir -p "$BASE_MODEL_DIR"

MAX_JOBS="${MAX_JOBS:-4}"
job_control() {
	while (( $(jobs -rp | wc -l) >= MAX_JOBS )); do
		wait -n
	done
}

# Generate ~/.s3cfg
generate_s3cfg() {
	cat > ~/.s3cfg <<EOF
[default]
access_key = ${AWS_ACCESS_KEY_ID}
secret_key = ${AWS_SECRET_ACCESS_KEY}
host_base = https://thanos-swift.discovery.wmnet
host_bucket = https://thanos-swift.discovery.wmnet
use_https = True
signature_v2 = False
EOF
}

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

download_models() {
	local url="$1"
	local dest_path="$2"

	if [ -f "$dest_path" ]; then
		log "File already downloaded: $dest_path, skiping."
		return 0
	fi

	if [ "${USE_S3CMD:-false}" = true ]; then
		log "Downloading using s3cmd: $url"
		s3cmd get "$url" "$dest_path"
	else
		log "Downloading using wget: $url"
		wget --no-verbose --show-progress --progress=bar:force:noscroll "$url" -O "$dest_path"
	fi
}

unpack_tgz() {
	local tgz_path="$1"
	local target_dir="$2"

	log "Extracting $tgz_path into $target_dir"
	mkdir -p "$target_dir"
	tar xvf "$tgz_path" -C "$target_dir" --strip-components=1
	rm -f "$tgz_path"
}

download_zipped_models() {
	local base_url="$1"
	local model_zip="$2"
	local dest_dir="$3"

	local model_dir="$dest_dir/${model_zip%.zip}"
	local zip_path="$dest_dir/$model_zip"

	if [ -d "$model_dir" ]; then
		log "$model_zip already extracted in $model_dir, skipping."
	else
		download_models "$base_url/$model_zip" "$zip_path"
		pushd "$dest_dir" > /dev/null
		unzip -o "$model_zip"
		rm -f "$model_zip"
		popd > /dev/null
	fi
}

if [ "${USE_S3CMD:-false}" = true ]; then
	log "Generating ~/.s3cfg ..."
	generate_s3cfg
fi

# List of models: name|subdir
TGZ_MODELS=(
	"nllb200-600M|nllb" # NLLB-200 big generic model
	"nllb-wikipedia|nllb" # Wikipedia optimized model with limited languages
	"madlad400-3b-ct2|madlad400" # MADLAD-400 NMT model
	"indictrans-en-indic|indictrans2" # Indictrans2 models for English to Indic languages
	"indictrans-indic-en|indictrans2" # Indictrans2 models for Indic languages to English
	"indictrans2-indic-indic|indictrans2" # Indictrans2 models for translating between Indic languages
)

for entry in "${TGZ_MODELS[@]}"; do
	IFS='|' read -r MODEL_NAME SUBDIR <<< "$entry"

	MODEL_TGZ="${MODEL_NAME}.tgz"
	MODEL_DIR="${BASE_MODEL_DIR}/${MODEL_NAME}"
	MODEL_URL="${BASE_URL}/${SUBDIR}/${MODEL_TGZ}"
	MODEL_TGZ_PATH="${BASE_MODEL_DIR}/${MODEL_TGZ}"

	if [ -d "$MODEL_DIR" ]; then
		log "$MODEL_NAME already extracted in $MODEL_DIR, skipping."
	else
		(
			download_models "$MODEL_URL" "$MODEL_TGZ_PATH"
			unpack_tgz "$MODEL_TGZ_PATH" "$MODEL_DIR"
		) &
		job_control
	fi
done

# OpusMT optimized model with limited languages
MODEL_BASE_URL="${BASE_URL}/opusmt"
OPUSMT_MODELS=(
	opusmt-en-bcl.zip opusmt-en-bi.zip opusmt-en-chr.zip opusmt-en-guw.zip
	opusmt-en-srn.zip opusmt-en-to.zip opusmt-en-ty.zip opusmt-en-ve.zip
	opusmt-sv-fi.zip opusmt-fr-ty.zip opusmt-en-fr-br.zip
)

for zip in "${OPUSMT_MODELS[@]}"; do
	download_zipped_models "$MODEL_BASE_URL" "$zip" "$BASE_MODEL_DIR" &
	job_control
done

# Softcatala models
MODEL_BASE_URL="${BASE_URL}/softcatala"
SOFTCATALA_MODELS=(
	softcatala-de-ca.zip softcatala-en-ca.zip softcatala-es-ca.zip softcatala-fr-ca.zip softcatala-gl-ca.zip
	softcatala-ca-de.zip softcatala-ca-en.zip softcatala-ca-es.zip softcatala-ca-fr.zip softcatala-ca-gl.zip
	softcatala-it-ca.zip softcatala-ja-ca.zip softcatala-nl-ca.zip softcatala-oc-ca.zip softcatala-pt-ca.zip
	softcatala-ca-it.zip softcatala-ca-ja.zip softcatala-ca-nl.zip softcatala-ca-oc.zip softcatala-ca-pt.zip
)

for zip in "${SOFTCATALA_MODELS[@]}"; do
	download_zipped_models "$MODEL_BASE_URL" "$zip" "$BASE_MODEL_DIR" &
	job_control
done

# Wait for all background jobs
wait

log "All models downloaded and extracted."
log "Starting server..."
# We exec in order to allow gunicorn to handle signals and not have them caught by bash
exec gunicorn "$@"
