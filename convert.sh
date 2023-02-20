rm -rf NLLB_ctranslate2
ct2-fairseq-converter \
    --model_path archive.wikipedia-distillated-20221216-115418/checkpoint.pt  \
    --data_dir ./archive.wikipedia-distillated-20221216-115418   \
    --output_dir NLLB_ctranslate2

cp  archive.wikipedia-distillated-20221216-115418/sentencepiece.bpe.model NLLB_ctranslate2