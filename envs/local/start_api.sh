#!/bin/bash

localstack_ip_address=$(docker inspect --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' localstack-main)

sam local start-api --env-vars ${0%/*}/local.json --skip-pull-image --add-host localstack.internal:$localstack_ip_address