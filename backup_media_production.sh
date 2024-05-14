#!/bin/bash
t=`sudo docker ps | grep django`
IFS=' ' read -ra my_array <<< "$t"
docker_id=$my_array

backup_filename="media_$(date +'%Y_%m_%dT%H_%M_%S').tar.gz"
sudo docker-compose -f production.yml exec tar -czvf ./backups_db/$backup_filename ./media
sudo docker cp $docker_id:/app/backups_db/$backup_filename ./backups/media/
