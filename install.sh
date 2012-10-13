#!/bin/bash
SCRIPT_NAME=`basename "$0"`
SCRIPT_PATH=${0%`basename "$0"`}
OLD_PATH_1="/home/${USER}/.local/share/rhythmbox/plugins/wikipedia/"
OLD_PATH_2="/home/${USER}/.local/share/rhythmbox/plugins/Wikipedia/"
PLUGIN_PATH="/home/${USER}/.local/share/rhythmbox/plugins/WikipediaSearch/"

rm -rf $OLD_PATH_1
rm -rf $OLD_PATH_2
rm -rf $PLUGIN_PATH

mkdir -p $PLUGIN_PATH
cp -r "${SCRIPT_PATH}"* "$PLUGIN_PATH"
rm "${PLUGIN_PATH}${SCRIPT_NAME}"

