#!/bin/bash

unset http_proxy
unset HTTP_PROXY
unset all_proxy
unset ALL_PROXY

delete()
{
    curl -i -X DELETE http://localhost:5000/v1/jobs/$1
}

create()
{
    curl -i \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -X POST \
    --data "{\"job\":{\"name\":\"$RANDOM\",\"jar\":\"file_mapped.jar\",\"deadline\":\"16/06/2013\",\"input\":\"s3://\",\"output\":\"s3://\",\"master\": {\"flavor\":\"t1.micro\"},\"slaves\": [{\"flavor\":\"t1.micro\",\"instances\":1},{\"flavor\":\"m1.small\",\"instances\":1}]}}" \
    http://localhost:5000/v1/jobs

}

get()
{
    curl -i http://localhost:5000/v1/jobs
}

info()
{
    curl -i http://localhost:5000/v1/jobs/$1
}

add()
{
    curl -i \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -X POST \
    --data "{\"slaves\": [{\"flavor\":\"t1.micro\",\"instances\":1}, {\"flavor\":\"m1.small\",\"instances\":1}]}" \
    http://localhost:5000/v1/jobs/$1/add
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
    add)
        add $2
        ;;
esac
