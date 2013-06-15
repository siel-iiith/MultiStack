#!/bin/bash
#curl --dump-header  -v -H "Accept: application/json" -H "Content-Type: application/json" -X POST --data "{\"uid\":12,\"token\":\"asdert\"}" http://localhost:5000/v1/
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
    --data "{\"cluster\":{\"name\":\"test\",\"node-recipes\": {\"tasktracker\":1,\"jobtracker\":1},\"image-id\":\"ubuntu-12.04-amd64.img\"}}" \
    http://localhost:5000/v1/clusters/

}

if [ ! -z $1 ]
then
    delete $1
else
    create
fi