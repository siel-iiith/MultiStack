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
    --data "{\"job\":{\"name\":\"$RANDOM\",\"jar\":\"s3://sieljars/hadoop-examples-1.1.2.jar\",\"args\":\"wordcount\",\"deadline\":\"16/06/2013\",\"input\":\"s3://hsinput\",\"output\":\"s3://hsoutput\",\"master\": {\"flavor\":\"m1.small\"},\"slaves\": [{\"flavor\":\"m1.medium\",\"instances\":1}]}}" \
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
    --data "{\"slaves\": [{\"flavor\":\"m1.small\",\"instances\":1}, {\"flavor\":\"m1.medium\",\"instances\":1}]}" \
    http://localhost:5000/v1/jobs/$1/add
}

rm()
{
    curl -i \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -X POST \
    --data "{\"slaves\": [{\"flavor\":\"m1.small\",\"instances\":1}, {\"flavor\":\"m1.medium\",\"instances\":1}]}" \
    http://localhost:5000/v1/jobs/$1/rm
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
    rm)
        rm $2
        ;;
esac
