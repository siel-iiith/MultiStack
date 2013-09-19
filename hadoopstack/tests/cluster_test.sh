#!/bin/bash

# ./cluster_test.sh <action>
# list -> Get a list of all clusters
# create -> Create a Cluster
# Delete -> Delete a Cluster

unset http_proxy
unset HTTP_PROXY
unset all_proxy
unset ALL_PROXY

delete()
{
    curl -X DELETE http://localhost:5000/v1/clusters/$1
}

create()
{
    curl \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -X POST \
    --data "{\"cluster\":{\"name\":\"$RANDOM\",\"master\": {\"flavor\":\"m1.small\",\"instances\":1},\"slave\": {\"flavor\":\"m1.small\",\"instances\":1},\"image-id\":\"ubuntu-12.04-amd64.img\"}}" \
    http://localhost:5000/v1/clusters
}

get()
{
    curl http://localhost:5000/v1/clusters
}

case $1 in
    list)
        get
        ;;
    create)
        create
        ;;
    delete)
        delete $2
        ;;
esac
