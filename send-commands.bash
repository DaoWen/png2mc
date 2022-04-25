set -e

target_pane=mc:mc3.0
target_pane=0:0

function send-line() {
    ( set +x; tmux send-keys -t "$target_pane" "$1" Enter )
    sleep 0.1
}

send-line 'gamerule sendCommandFeedback false'
while read LINE; do
    send-line "$LINE"
done
send-line 'gamerule sendCommandFeedback true'

