docker run \
    -v $(pwd):/usr/src/app \
    -w /usr/src/app \
    -it \
    --rm \
    python:3.11-slim \
    bash