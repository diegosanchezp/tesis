load_env(){
  set -a
  source ${1:-.env}
}

REPODIR="$HOME/tesis"

[ -d "$REPODIR" ] && load_env "$REPODIR"/envs/production/host
