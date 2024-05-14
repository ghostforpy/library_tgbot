#!/bin/bash
sudo docker images | grep none | awk '{ print $3; }' | sudo xargs docker rmi --force
