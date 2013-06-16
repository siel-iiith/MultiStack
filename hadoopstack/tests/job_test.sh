#!/bin/bash
#curl --dump-header  -v -H "Accept: application/json" -H "Content-Type: application/json" -X POST --data "{\"uid\":12,\"token\":\"asdert\"}" http://localhost:5000/v1/
unset http_proxy
unset HTTP_PROXY
unset all_proxy
unset ALL_PROXY

delete()
{
    curl -X DELETE http://localhost:5000/v1/jobs/$1
}

create()
{
    curl \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -X POST \
    --data "{\"jobs\":{\"name\":\"my-job\",\"jar\":\"file_mapped.jar\",\"deadline\":\"16/06/2013\",\"input\":\"Swift/S3\",\"output\":\"Swift/S3\",\"master\": {\"flavor\":\"m1.medium\",\"instances\":1},\"slave\": {\"flavor\":\"m1.large\",\"instances\":2} }}" \
    http://localhost:5000/v1/jobs/

}

if [ ! -z $1 ]
then
    delete $1
else
    create
fi
