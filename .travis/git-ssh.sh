#!/bin/sh

ssh -i .travis/deploy_key -o PasswordAuthentication=no -p 2222 $1 $2 $3 $4
