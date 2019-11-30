#! /bin/sh -
PROGNAME=$0

usage() {
cat << EOF >&2
Usage: ${PROGNAME} [-c] [-r]
-c: create stack using the multi-service yml file
-r: remove stack (runs docker stack rm)
EOF
  exit 1
}
if [ $# -eq 0 ]; then
    usage
fi
isRm=0 isCreate=0
while getopts ":cr" opt; do
  case $opt in
    (r) isRm=1;;
    (c) isCreate=1;;
    (*) usage
  esac
done
if [ $isRm -eq 1 ]; then
    docker stack rm task2;
fi

if [ $isCreate -eq 1 ]; then
    docker stack deploy -c multi-service-app.yml task2
    echo "host $(docker node inspect --format="{{json .Status.Addr}}" self) running on port 80"
    exit;
fi

