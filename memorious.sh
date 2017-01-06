#!/bin/sh

set -e

key="$HOME/.memorious/memorious.key"
mem="$HOME/.memorious/memorious.mem"

gpg="/usr/bin/gpg --quiet --batch --passphrase-file $key --armor"
encrypt="$gpg --symmetric --cipher-algo AES256 -o $mem"
decrypt="$gpg --decrypt $mem"

tmp=$(mktemp /tmp/memorious.mem.XXXXXX)
exec 3>"$tmp"
rm "$tmp"

cmd="$1"
shift

args=$(getopt -u -o xd:u:p:c: -l copy,domain:,username:,password:,comment: -- $*)
set -- $args

opt_copy=
domain=
comment=
username=
password=
while true; do
  case "$1" in
    -x | --copy)     opt_copy=1;  shift;;
    -d | --domain)     domain=$2; shift 2;;
    -c | --comment)   comment=$2; shift 2;;
    -u | --username) username=$2; shift 2;;
    -p | --passname) passname=$2; shift 2;;
    --) shift; break;;
  esac
done

rand() {
  base64 /dev/urandom | head -c $1
}

new_cmd() {
  if [ -e "$key" ]; then
    echo "Error: keyfile '$key' exists"; exit 1
  fi
  mkdir -p $(dirname $key)
  rand 1024 > $key
}

get_cmd() {
  res=$($decrypt)
  if [ -n "$domain" ]; then
    res=$(echo "$res" | grep "^$domain;")
  fi
  if [ -n "$opt_copy" ]; then
    echo "$res" | awk -F ";" 'END { printf "%s", $3 }' | xclip -i
    out=$(echo "$res" | awk -F";" '{ print $1 " " $2 " *copied* " $4 }')
  else
    out=$(echo "$res" | awk -F";" '{ print $1 " " $2 " " $3 " " $4 }')
  fi
  echo -e "domain username password comment\n$out" | column -t
}

set_cmd() {
  if [ -z "$password" ]; then
    password=$(rand 16)
    if [ -n "$opt_copy" ]; then
      echo "Generated password: *copied*"
      echo $password | xclip -i
    else
      echo "Generated password: $password"
    fi
  fi
  comment="$4"
  if [ -e $mem ]; then
    $decrypt >&3
    rm $mem
  fi
  echo "$domain;$username;$password;$comment" >&3
  $encrypt /dev/fd/3
}

edit_cmd() {
  $decrypt >&3
  $EDITOR /dev/fd/3
  rm $mem #TODO: do this only if next command succeed
  $encrypt /dev/fd/3
}

export_cmd() {
  $decrypt
}

import_cmd() {
  cat /dev/fd/0 > /dev/fd/3
  $encrypt /dev/fd/3
}

case "$cmd" in
  n | new)  new_cmd;;
  g | get)  get_cmd;;
  s | set)  set_cmd;;
  e | edit) edit_cmd;;
  export)   export_cmd;;
  import)   import_cmd;;
  *)        echo "Usage: $0 {new|get|set|edit|dump|export|import}"; exit 1
esac
