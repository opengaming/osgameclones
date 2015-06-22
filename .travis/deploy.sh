#!/bin/sh

set -ev

test "${TRAVIS_PULL_REQUEST}" = "false" || exit 0

openssl aes-256-cbc -K $encrypted_61da1a775a65_key -iv $encrypted_61da1a775a65_iv -in .travis/deploy_key.enc -out .travis/deploy_key -d
chmod 600 .travis/deploy_key
eval $(ssh-agent -s)
ssh-add .travis/deploy_key
git remote add maia dokku@maia.solovyov.net:osgc
git push maia master
