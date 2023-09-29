load_env(){
  set -a
  source ${1:-.env}
}
