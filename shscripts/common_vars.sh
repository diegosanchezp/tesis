SCRIPT_FILE_PATH=$(realpath "${BASH_SOURCE[0]:-$0}")
SCRIPT_DIR=$(dirname "$SCRIPT_FILE_PATH")
# ../../
ROOT_DIR=$(dirname "$SCRIPT_DIR")
COMPOSE_FILE=$ROOT_DIR/docker/dev/docker-compose.yml
export COMPOSE_FILE
