#!/bin/bash
#curl --dump-header  -v -H "Accept: application/json" -H "Content-Type: application/json" -X POST --data "{\"uid\":12,\"token\":\"asdert\"}" http://localhost:5000/v1/
export http_proxy=''

curl --dump-header  -v -H "Accept: application/json" -H "Content-Type: application/json" -X POST --data "{\"cluster\": {\"node-recipes\": {\"tasktracker\": 3, \"jobtracker\": 1}, \"name\": \"test\", \"image-id\": \"ubuntu-12.04-amd64.img\"}}"  http://localhost:5000/v1/clusters/

