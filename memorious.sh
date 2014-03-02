#!/bin/sh

dir="$HOME/.memorious2"
key="$dir/memorious.key"
mem="$dir/memorious.mem"
csv="$dir/memorious.csv"

function usage {
  echo
  echo "Commands: new get put del"
}

# Init
case "$1" in
  "new")
    mkdir $dir

    touch $key
    chmod 600 $key
    dd if=/dev/urandom count=1 bs=256 | base64 > $key
    chmod 400 $key

    touch $mem
    chmod 600 $mem
    ;;
esac

# Open
touch $csv
chmod 600 $csv
base64 --decode $key | openssl aes-256-cbc -d \
  -md sha512 -base64 -salt -pass stdin -in $mem -out $csv

# Use
case "$1" in
  "new")
    echo "domain,username,password" > $csv
    ;;
  "get")
    grep "$2" $csv
    # TODO: if --copy then cut -f3 -d, | tail -1 | xclip -i
    ;;
  "put")
    if [ "$2" = "-" ]; then # Reading from stdin
      cat >> $csv
    else
      if [ -z "$2" ]; then # Interactive mode
        read -p "Domain: " domain
      else
        domain=$2
      fi

      if [ -z "$3" ]; then # Interactive mode
        read -p "Username: " username
      else
        username=$3
      fi

      if [ -z "$4" ]; then # Interactive mode
        stty -echo
        read -p "Password: " password
        stty echo
        echo
      else
        password=$4
      fi
      if [ -z "$password" ]; then
        password=$(pwgen --secure 16 1)
      fi

      echo "$domain;$username;$password" >> $csv
    fi
    ;;
  "")
    echo "memorious: no command given."
    usage
    ;;
  *)
    echo "memorious: '$1' is an invalid command."
    usage
    ;;
esac

# Close
base64 --decode $key | openssl aes-256-cbc -e \
  -md sha512 -base64 -salt -pass stdin -in $csv -out $mem
rm $csv
