# Android Device Testing Framework ("dtf")
# Copyright 2013-2015 Jake Valletta (@jake_valletta)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Bash Completion Script

getroot () {

    if [ -f .dtfini ]; then echo "$PWD" && return; fi

    test / == "$PWD" && return || test -e "$1" && echo "$PWD" && return || cd .. && upsearch ".dtfini"
}

upsearch () {
    test / == "$PWD" && return || test -e "$1" && echo "$PWD" && return || cd .. && upsearch "$1"
}

_dtf()
{
    MAIN_DB=~/.dtf/main.db

    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts=""

    TOP=$(getroot)

    CORE="archive client help init local modules pm prop reset shell status"
    MODULES=$(sqlite3 "${MAIN_DB}" "select name from modules" 2>/dev/null|tr '\n' ' ')
    LOCAL_MODULES=$(ls "${TOP}/local_modules" 2>/dev/null)

    opts="${CORE} ${MODULES} ${LOCAL_MODULES}"

    if [[ ${cur} == -* || ${COMP_CWORD} -eq 1 ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    else
        COMPREPLY=( $(compgen -W "`ls`" -- ${cur}) )
        return 0
    fi


}
complete -F _dtf dtf
