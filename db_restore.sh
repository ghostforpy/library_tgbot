#!/bin/bash
backup_filename=$1

sudo docker cp ./backups/$backup_filename $(docker-compose -f production.yml ps -q postgres):/backups/$backup_filename

sudo docker-compose -f production.yml exec postgres restore $backup_filename