# iob-dash

The docker image iob-dash provides a python application to visualize meter readings stored by the iobroker-sql adapter into a mariadb / mysql database.
The container needs only read access to the database and no direct access to IOBroker itself.

The values are written to the database by the iobroker sql-adapter (https://github.com/ioBroker/ioBroker.sql).
In order to query all meters by name, a corresponding alias for the data points must be assigned in the sql adapter:
alias-counter-METERNAME
(alias-counter-gas, alias-counter-water....)


## create docker image
change into repo folder 
```
docker build -f Dockerfile -t iob-dash .
```

## start container
```
docker run --name iob-dash -d \
    --hostname iob-dash \
    --network=private-net \
    --ip=192.168.0.15  \
    --dns=192.168.0.254  \
    -v /var/lib/docker/configs/iob-dash:target=/certs \
    -e DB_HOST=localhost \
    -e DB_USER=iobroker \
    -e DB_PASSWORD=SECRET \
    --restart unless-stopped \
    iob-dash:latest
```