_dtf()
{
    . dtf_core.sh

    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts=""

    CORE="config delprop getprop help init local modules pm reset setprop shell status"
    MODULES=$(sqlite3 ${DTF_DIR}/main.db "select name from modules"|tr '\n' ' ')
    opts="${CORE} ${MODULES}"

    if [[ ${cur} == -* || ${COMP_CWORD} -eq 1 ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    else
        COMPREPLY=( $(compgen -W "`ls`" -- ${cur}) )
        return 0
    fi


}
complete -F _dtf dtf
