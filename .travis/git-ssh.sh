#!/bin/sh

ssh -i .travis/deploy_key -o UserKnownHostsFile=.travis/known_hosts -o PasswordAuthentication=no $1 $2 $3 $4
