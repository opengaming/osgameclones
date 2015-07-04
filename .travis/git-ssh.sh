#!/bin/sh

ssh -i .travis/deploy_key -o PasswordAuthentication=no $1 $2 $3 $4
