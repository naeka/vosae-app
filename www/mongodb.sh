#!/bin/bash

RETVAL=0
DBPATH="./databases"
DBLOCK="$DBPATH/mongod.lock"

bold=`tput bold`
normal=`tput sgr0`

usage() {
    echo """${bold}SYNOPSIS${normal}
      $0 <command>

${bold}COMMANDS${normal}
      ${bold}start${normal}
          start mongod instance

      ${bold}stop${normal}
          stop mongod instance

      ${bold}restart${normal}
          restart mongod instance

      ${bold}cleandb${normal}
          1. stop mongod instance
          2. remove all databases present in dbpath ($DBPATH)
          3. start mongod instance
"""
}

start_mongod() {
    mongod --dbpath $DBPATH --noprealloc --nojournal --rest --directoryperdb --smallfiles --nssize 2 &
    echo "MongoDB started"
}

stop_mongod() {
    mongod --dbpath $DBPATH --shutdown
    echo "MongoDB stopped"
}

check_lock() {
    if [[ -s $DBLOCK ]]; then
        echo "A database lock is present."
        PID=`cat $DBLOCK`
        if [[ -z `ps -o pid= -o comm= -p $PID` ]]; then
            echo -n "Would you force lock deletion? [y/N] "
            read force_delete
            if [[ $force_delete == "y" ]]; then
                echo -n > $DBLOCK
                return
            fi
        else
            echo "Maybe the database is running."
            echo -n "Would you try to stop it before? [y/N] "
            read does_stop
            if [[ $does_stop == "y" ]]; then
                stop_mongod
                return
            fi
        fi
        echo "Error occured. Exiting..."
        exit 1
    fi
}

clean_dbs() {
    rm -rf "$DBPATH/*"
    echo "MongoDB cleaned"
}

case "$1" in
    cleandb)
        stop_mongod
        clean_dbs
        start_mongod
        ;;
    restart)
        stop_mongod
        start_mongod
        ;;
    stop)
        stop_mongod
        ;;
    start)
        check_lock
        start_mongod
        ;;
    *)
        usage
        RETVAL=1
esac

exit $RETVAL
