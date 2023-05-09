# MinT machine translation system

**MinT** is a machine translation system hosted by Wikimedia Foundation.
It uses [NLLB](https://ai.facebook.com/research/no-language-left-behind/) and
[OpusMT](https://github.com/Helsinki-NLP/OPUS-MT) language models for translation.
The models are optimized for performance using [OpenNMT CTranslate2](https://github.com/OpenNMT/CTranslate2)

## Usage

### Installation
Clone the repository, create a virtual environment and install dependencies

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

* `CT2_INTER_THREADS`: maximum number of batches executed in parallel. Refer https://opennmt.net/CTranslate2/parallel.html. Default is `1`
* `CT2_INTRA_THREADS`: number of computation threads that is used per batch Refer https://opennmt.net/CTranslate2/parallel.html. Default is `1`

For above configurations, Use a value less than or equal to the available CPU cores.

### Monitoring

Application can be monitored using graphite.
Dun the graphite-statsd docker, and point the statsd-host to it

```bash
docker run -d\
 --name graphite\
 --restart=always\
 -p 80:80\
 -p 2003-2004:2003-2004\
 -p 2023-2024:2023-2024\
 -p 8125:8125/udp\
 -p 8126:8126\
 graphiteapp/graphite-statsd

```

Now set the env value `STATSD_HOST` to `localhost` and  `STATSD_PORT` to 8125. STATSD_PREFIX environment variable can be used to override the default
"machinetranslation" prefix.

Example:
```
STATSD_HOST=127.0.0.1 gunicorn
```
