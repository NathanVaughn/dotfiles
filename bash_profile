# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
	. ~/.bashrc
fi

# User specific environment and startup programs

PATH=$PATH:$HOME/.local/bin:$HOME/bin

export PATH

export PS1="\[\033[38;5;196m\]\u\[$(tput sgr0)\]\[\033[38;5;15m\]@\[$(tput sgr0)\]\[\033[38;5;40m\]\h\[$(tput sgr0)\]\[\033[38;5;15m\]:\[$(tput sgr0)\]\[\033[38;5;87m\][\[$(tput sgr0)\]\[\033[38;5;39m\]\w\[$(tput sgr0)\]\[\033[38;5;51m\]]\[$(tput sgr0)\]\[\033[38;5;226m\]\\$\[$(tput sgr0)\]\[\033[38;5;15m\] \[$(tput sgr0)\]"

# export LS_OPTIONS='--color=auto'
# eval "$(dircolors -b)"
# alias ls='ls $LS_OPTIONS'

eval $(dircolors -b $HOME/.dircolors)
