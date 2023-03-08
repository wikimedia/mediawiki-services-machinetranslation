# Wikipedia machine translation system

```
docker build -t wikipedia-mt .
docker run -dp 3000:80 wikipedia-mt:latest
```

Open http://0.0.0.0:3000/ using browser


## Monitoring

Application can be moniotred using graphite.
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

Now change the `statsd_host` in gunicorn.conf.py or use --statsd-host commandline option of gunicorn.

