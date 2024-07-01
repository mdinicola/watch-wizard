#!/bin/bash

. ${0%/*}/env_vars.sh

localstack start --detached

aws --endpoint-url http://localhost:4566 secretsmanager create-secret --name apps/WatchWizard --secret-string "{\"AlexaSkillId\": \"${ALEXASKILLID}\", \"PlexUsername\": \"${PLEXUSERNAME}\", \"PlexPassword\": \"${PLEXPASSWORD}\", \"PlexServerName\": \"${PLEXSERVERNAME}\", \"TraktClientId\": \"${TRAKTCLIENTID}\", \"TraktClientSecret\": \"${TRAKTCLIENTSECRET}\", \"TraktOauthToken\": \"${TRAKTOAUTHTOKEN}\", \"TraktOauthRefreshToken\": \"${TRAKTOAUTHREFRESHTOKEN}\", \"TraktOauthExpiryDate\": ${TRAKTOAUTHEXPIRYDATE}}"

