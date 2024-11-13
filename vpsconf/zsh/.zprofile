load_env(){
  set -a
  source ${1:-.env}
}

REPODIR="$HOME/repos/tesis"

[ -d "$REPODIR" ] && load_env "$REPODIR"/envs/production/host
