# zone-monitor

Monitors Certificate Transparency log for suspicious websites and takes screenshots of them.

## How to run
```
docker-compose up --build --scale chrome=3 --scale worker=3
```

## Reset state (destroy all volumes)
```
docker-compose down -v
```

## Copyrights

2019 CERT.PL, CSIRT.CZ

