#!/bin/bash

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 571600842832.dkr.ecr.us-east-1.amazonaws.com
echo "logging in..."

echo "what do you want your image to be called?"
read myimagename

echo "Image name is: $myimagename"

echo "what is the repo name?"
read myreponame

echo "repo is $myreponame"

docker build -t $myimagename .
echo "building image..."

docker tag $myimagename:latest 571600842832.dkr.ecr.us-east-1.amazonaws.com/$myreponame:latest
echo "tagging image..."
docker push 571600842832.dkr.ecr.us-east-1.amazonaws.com/$myreponame:latest
echo "pushing image to ECR..."