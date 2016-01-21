# -------- Color ----------------------------------------------

red='\e[0;31m'
RED='\e[1;31m'
blue='\e[0;34m'
BLUE='\e[1;34m'
cyan='\e[0;36m'
CYAN='\e[1;36m'
green='\e[0;32m'
GREEN='\e[1;32m'
pink='\e[0;35m'
PINK='\e[1;35m'
NC='\e[0m'

# ---- PATH ----------------------------------------

addpath() {
  local val
  val=`eval 'echo $'"$2"`
  if [ -d $3 ]; then
    case  "$val" in
     "") eval "${2}=${3}" ;;
      *:$3|*:${3}:*|${3}:*|${3}) ;;
      *)
      case "$1" in
         prepend) eval "${2}=${3}:${val}" ;;
         append)  eval "${2}=${val}:${3}" ;;
      esac
      ;;
    esac
  fi

  eval "export $2"
}


append() {
    addpath append $1 $2
}

prepend() {
    addpath prepend $1 $2
}

delpath() {
    local val sedscr
    val=`eval 'echo $'"$1"`
    sedscr="s%^${2}:%%;s%:${2}:%:%g;s%:$2$%%;s%^${2}$%%;"
    eval "$1=`echo $val | sed -e $sedscr`"
    val=`eval 'echo $'"$1"`
    eval "if [ \"\$$1\" = \"\" ]; then unset $1; fi"
}



## Shell Vars
export PS1="\[\033[32m\][\u]\[\033[0m\] \e]2;\u@\H\a"
export PS2="continue-> "
export PATH=$PATH:$HOME/bin
export VIMHOME=$HOME/.vim
shopt -s cdable_vars
export HOST=$(hostname)
export OS=$(uname)
export HISTIGNORE="ls -las:ls:exiti:history:pwd"
export HISTCONTROL=ignoredups

 #Alias
if [ "$OS" = "Linux" ]; then
    alias ls="ls --color=auto -h"
   elif [ "$OS" = "Darwin" ]; then
    alias ls="ls -G"
fi

#alias subl="/Applications/Sublime\ Text.app/Contents/MacOS/Sublime\ Text"
#alias venv="source ./venv/bin/activate"

slog() {
    con='ssh -Y'
    case $1 in
        "jenkins")    $con sp6  ;; 
        "git")        $con sp11 ;;
        "zenoss")     $con sp12 ;;
        "confluence") $con sp15 ;;
        "crusible")   $con sp16 ;;
        "itop")       $con sp22 ;;
        "stash")      $con sp23 ;;
        "sp31")       $con sp31 ;;
        "sp32")       $con sp32 ;;
        "sensuc")     $con sp48 ;;
        "sensui")     $con sp49 ;;
        "grafana")    $con sp50 ;;
        "graphite")   $con sp51 ;;
        "jira")       $con jira ;;
        "cfg1")       $con cfg1 ;;
        "sp54")       $con sp54 ;;
        "sp56")       $con sp56 ;;
        "sp13")       $con sp13 ;;
        "sp5")        $con sp5 ;;
        "sp18")       $con sp18 ;;
        "itop")       $con sp22 ;;
        "sp36")       $con sp36 ;;
        "sp43")       $con sp43 ;;
        "grape")      $con grape ;;

        *) echo "Unknown Host ID: Please specify a known server name";;  
    esac
}

tunnel() {
  con='ssh -f -N'
  case $1 in
    "st119")  $con st119 ;;
    "elk69")  $con elk69 ;;
    "elk70")  $con elk70 ;;
    "elk71")  $con elk71 ;;

    *) echo "Unknown Host ID: Please specify a known server name";;  
  esac
}

# Version Control Systems
export SVN_EDITOR=vim
export CVS_RSH=ssh
export GIT_EDITOR=vim

#virt() {
#cd ~/flask_dev/flasky/
#export PS1=":~# "
#source venv/bin/activate
#echo "Flask Development Environment: Enabled"
#}

touch ~/.bash_log
echo "["$(date)"] - $USER Logged in from shell" >> ~/.bash_log

# AD Admin Login
export DOMIAN_ADM=ab2-admin@realvnc.ltd

# Functions

function showssh {
  echo "Printing SSH Connections"
  ps -ef | grep ssh
  echo ""
  lsof -i -n | egrep '\<ssh\>'
}
