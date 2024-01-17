# MinT machine translation system

**MinT** is a machine translation system hosted by Wikimedia Foundation.
It uses multiple Neural Machine translation models to provide translation between large number of languages.

Currently used models:

* [NLLB](https://ai.facebook.com/research/no-language-left-behind/)
* [OpusMT](https://github.com/Helsinki-NLP/OPUS-MT)
* [SoftCatala](https://github.com/Softcatala/nmt-models)
* [IndicTrans2](https://github.com/AI4Bharat/IndicTrans2)
* [MADLAD-400](https://huggingface.co/google/madlad400-3b-mt)

The models are optimized for performance using [OpenNMT CTranslate2](https://github.com/OpenNMT/CTranslate2)

## Usage

### Installation

Clone the repository. Install the system dependencies:

```bash
sudo apt install wget unzip build-essential cmake
```

Create a python virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then run the service:

```bash
./entrypoint.sh
```

By default it will run in `http://0.0.0.0:8989`.

### Using docker

Clone the repository, build the docker image and run it.

```bash
docker build -t wikipedia-mt .
docker run -dp 8989:8989 wikipedia-mt:latest
```

Open http://0.0.0.0:8989/ using browser

## Environment variables

* `CT2_INTER_THREADS`: maximum number of batches executed in parallel. Refer https://opennmt.net/CTranslate2/parallel.html. Default is number of CPUs.
* `CT2_INTRA_THREADS`: number of computation threads that is used per batch Refer https://opennmt.net/CTranslate2/parallel.html. Default is `0`(auto)

For above configurations, Use a value less than or equal to the available CPU cores.

### Monitoring

Application can be monitored using graphite.
Run the graphite-statsd docker, and point the statsd-host to it

```bash
docker run -d \
 --name graphite \
 --restart=always \
 -p 80:80 \
 -p 2003-2004:2003-2004 \
 -p 2023-2024:2023-2024 \
 -p 8125:8125/udp \
 -p 8126:8126 \
 graphiteapp/graphite-statsd

```

Now set the env value `STATSD_HOST` to `localhost` and  `STATSD_PORT` to 8125. STATSD_PREFIX environment variable can be used to override the default
"machinetranslation" prefix.

Example:
```
STATSD_HOST=127.0.0.1 gunicorn
```

## License

MinT is licensed under MIT license. See [License.txt](./LICENSE.txt)

MinT uses multiple machine translation models internally.

* NLLB models are licensed under [CC-BY-NC](https://creativecommons.org/licenses/by-nc/4.0/).
* OpusMT models are licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
* Softcatala models are [MIT licensed](https://github.com/Softcatala/nmt-models/blob/master/LICENSE).
* IndicTrans2 models are [MIT licensed](https://github.com/AI4Bharat/IndicTrans2)
* MADLAD-400 models are [Apache 2.0 licensed](https://huggingface.co/google/madlad400-3b-mt)
