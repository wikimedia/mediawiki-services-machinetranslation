import ctranslate2
from sentencepiece import SentencePieceProcessor
import time
import multiprocessing

src_lang="__eng__"
tgt_lang="__ibo__"

sentences = """
Jazz is a music genre that originated in the African-American communities of New Orleans, Louisiana, United States, in the late 19th and early 20th centuries, with its roots in blues and ragtime.
Since the 1920s Jazz Age, it has been recognized as a major form of musical expression in traditional and popular music, linked by the common bonds of African-American and European-American musical parentage.
Jazz is characterized by swing and blue notes, complex chords, call and response vocals, polyrhythms and improvisation.
Jazz has roots in West African cultural and musical expression, and in African-American music traditions.
""".strip().splitlines()

tokenizer = SentencePieceProcessor()
tokenizer.load('models/nllb-wikipedia/sentencepiece.bpe.model')

translator = ctranslate2.Translator(
   "models/nllb-wikipedia",
   # maximum number of batches executed in parallel.
   # => Increase this value to increase the throughput.
   #inter_threads=multiprocessing.cpu_count(),
   #  number of OpenMP threads that is used per batch.
   # => Increase this value to decrease the latency on CPU.
   #intra_threads=multiprocessing.cpu_count(),
   device="auto",
   compute_type='int8'
)

start_time=time.time()
sentences_tokenized=[]
for sentence in sentences:
   sentences_tokenized.append(
      [tgt_lang]+tokenizer.encode(sentence, out_type=str) + ['</s>']
   )
results = translator.translate_iterable(
   sentences_tokenized,
   asynchronous=True,
   batch_type="tokens",
   max_batch_size=1024,
   beam_size=1,
)

for result in results:
    print(tokenizer.decode(result.hypotheses[0][1:]))
print(f"Translated in {time.time()-start_time}")