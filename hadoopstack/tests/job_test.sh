#!/bin/bash

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
    --data "{\"job\":{\"name\":\"$RANDOM\",\"jar\":\"file_mapped.jar\",\"deadline\":\"16/06/2013\",\"input\":\"s3://\",\"output\":\"s3://\",\"master\": {\"flavor\":\"m1.small\"},\"slaves\": [{\"flavor\":\"m1.small\",\"instances\":1}, {\"flavor\":\"m1.large\",\"instances\":1}]}}" \
    http://localhost:5000/v1/jobs

}

get()
{
    curl http://localhost:5000/v1/jobs
}

info()
{
    curl http://localhost:5000/v1/jobs/$1
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
    info)
        info $2
        ;;
esac
