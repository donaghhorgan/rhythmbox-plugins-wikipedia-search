#!/usr/bin/env bash
# Installs the WikipediaSearch plugin for Rhythmbox
# Copyright (C) 2016 Donagh Horgan <donagh.horgan@gmail.com>

name=WikipediaSearch
path=~/.local/share/rhythmbox/plugins/$name
files=( LICENSE $name.plugin $name.py README.md )

if [ -d "$path" ]; then
  rm -rf $path
fi

mkdir -p $path

for file in "${files[@]}"
do
  cp $file $path
done

