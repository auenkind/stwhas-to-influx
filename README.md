# Stwhas to influx
Docker Image for copying Stadtwerke Haßfurt Smart power meter data to influx

Uses [stwhas-python-api-client](https://github.com/auenkind/stwhas-python-api-client) to fetch the data.

## Build Container
```bash
docker build -t stwhas-to-influx .
```
## Run Container (by cron.daily)

```bash
docker run stwhas-to-influx -u <mailaddress> -p <password> -m <meter_number> -ih <influx_host> -it <influx_token> -io <influx_org> -ib <influx_bucket>
```