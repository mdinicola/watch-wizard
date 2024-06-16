#!/bin/bash

. ${0%/*}/env_vars.sh

localstack start --detached

aws --endpoint-url http://localhost:4566 secretsmanager create-secret --name apps/WatchWizard-Trakt --secret-string "{\"CLIENT_ID\": \"${TRAKTCLIENTID}\", \"CLIENT_SECRET\": \"${TRAKTCLIENTSECRET}\", \"OAUTH_TOKEN\": \"${TRAKTOAUTHTOKEN}\", \"OAUTH_REFRESH\": \"${TRAKTOAUTHREFRESH}\", \"OAUTH_EXPIRES_AT\": ${TRAKTOAUTHEXPIRESAT}}"

aws --endpoint-url http://localhost:4566 secretsmanager create-secret --name apps/WatchWizard --secret-string "{\"AlexaSkillId\": \"${ALEXASKILLID}\", \"PlexUsername\": \"${PLEXUSERNAME}\", \"PlexPassword\": \"${PLEXPASSWORD}\", \"PlexServerName\": \"${PLEXSERVERNAME}\"}"