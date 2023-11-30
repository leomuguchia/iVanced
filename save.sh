#!/bin/bash

rm -rf ~/.ssh/known_hosts

cd "$(dirname "$0")" || exit

run_ssh_command() {
  sshpass -p 'alpine' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost -p2222 "$@"
}

copy_files() {
  sshpass -p 'alpine' scp -rP 2222 -o StrictHostKeyChecking=no root@localhost:"$1" "$2"
}

log() {
  echo "$(date +"%H:%M:%S") - $1"
}

mkdir -p ./files

iproxy 2222:22 > /dev/null 2>&1 &

log "Mounting"
if ! run_ssh_command 'mount_filesystems'; then
  log "Error: Failed to mount filesystems"
fi
log "Mounted!"

if ! copy_files "/mnt2/containers/Data/System/*/Library/activation_records/activation_record.plist" ./files/; then
  log "Error: Failed to copy activation_record.plist"
fi

if ! copy_files "/mnt2/containers/Data/System/*/Library/internal/data_ark.plist" ./files/; then
  log "Error: Failed to copy data_ark.plist"
fi

if ! copy_files "/mnt2/mobile/Library/FairPlay/" ./files/; then
  log "Error: Failed to copy FairPlay folder"
fi

if ! copy_files "/mnt2/wireless/Library/Preferences/com.apple.commcenter.device_specific_nobackup.plist/" ./files/; then
  log "Error: Failed to copy com.apple.commcenter.device_specific_nobackup.plist"
fi

if ! run_ssh_command '/sbin/reboot'; then
  log "Error: Failed to reboot"
fi

log "Activation files saved!"
kill %1 > /dev/null 2>&1
