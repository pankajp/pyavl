#! /usr/bin/env bash
echo $1
avl $1 < geominp
mv plot.ps $1.ps

