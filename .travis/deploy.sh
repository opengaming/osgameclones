#!/bin/sh

set -ev

if [ "${TRAVIS_PULL_REQUEST}" = "false" ]; then
    openssl aes-256-cbc -K $encrypted_61da1a775a65_key -iv $encrypted_61da1a775a65_iv -in .travis/deploy_key.enc -out .travis/deploy_key -d
    chmod 600 .travis/deploy_key
    git remote add maia dokku@maia.solovyov.net:osgc
    GIT_SSH=".travis/deploy.sh" git push maia master
fi
