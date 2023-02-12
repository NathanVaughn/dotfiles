#!/bin/bash

alias clc='clear'
alias cls='clear'

alias ll='ls -la'
alias bat='batcat'
alias w='watch'

alias ..='cd ..'
alias ....='cd ../..'
alias ......='cd ../../..'

alias ipconfig='ifconfig'

alias activate='source ./.venv/bin/activate'
alias venv='python -m venv .venv'
alias guid='cat /proc/sys/kernel/random/uuid'

alias please='sudo'
alias ugh='sudo $(history -p !!)'