#!/bin/sh

curl -X POST -H 'Content-Type:application/json' -d "@send_on.json" "http://localhost:8000/command"
