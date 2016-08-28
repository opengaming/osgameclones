#!/bin/bash

set -ev

openssl aes-256-cbc -K $encrypted_61da1a775a65_key -iv $encrypted_61da1a775a65_iv -in .travis/deploy_key.enc -out .travis/deploy_key -d
chmod 600 .travis/deploy_key

GIT_SSH=".travis/git-ssh.sh" git push dokku@sirius.solovyov.net:osgc master
