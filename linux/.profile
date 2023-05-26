#!/bin/bash

# ~/.profile: executed by the command interpreter for login shells.

# This file is not read by bash(1), if ~/.bash_profile or ~/.bash_login
# exists.  Note, however, that we will have a ~/.bash_profile and it
# will simply source this file as a matter of course.

# See /usr/share/doc/bash/examples/startup-files for examples.
# The files are located in the bash-doc package.

export PYENV_ROOT="$HOME/.pyenv"

export PATH=~/bin:$PATH
export PATH=~/.local/bin:$PATH
export PATH="$PYENV_ROOT/bin:$PATH"

# for pyenv
if command -v pyenv &> /dev/null
then
    eval "$(pyenv init -)"
fi

