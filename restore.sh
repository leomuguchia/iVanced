#!/bin/bash

rm -rf ~/.ssh/known_hosts

cd "$(dirname "$0")" || exit

log() {
  echo "$(date +"%H:%M:%S") - $1"
}

run_ssh_command() {
  sshpass -p 'alpine' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost -p4444 "$@"
}

copy_files() {
  sshpass -p 'alpine' scp -rP 4444 -o StrictHostKeyChecking=no "$1" root@localhost:"$2"
}

log "Mounting"
if ! run_ssh_command 'mount -o rw,union,update /'; then
  log "Error: Failed to mount filesystem"
fi
log "Mounted!"

log "Cleaning up"
run_ssh_command 'rm -rf /var/mobile/Media/Downloads/1'
run_ssh_command 'rm -rf /var/mobile/Media/1'
run_ssh_command 'mkdir /var/mobile/Media/Downloads/1'

log "Copying files"
copy_files "./files" "/var/mobile/Media/Downloads/1"

log "Moving files"
run_ssh_command 'mv -f /var/mobile/Media/Downloads/1 /var/mobile/Media'

log "Setting permissions"
run_ssh_command 'chown -R mobile:mobile /var/mobile/Media/1'
run_ssh_command 'chmod -R 755 /var/mobile/Media/1'
run_ssh_command 'chmod 644 /var/mobile/Media/1/files/activation_record.plist'
run_ssh_command 'chmod 644 /var/mobile/Media/1/files/data_ark.plist'
run_ssh_command 'chmod 644 /var/mobile/Media/1/files/com.apple.commcenter.device_specific_nobackup.plist'

log "Moving FairPlay folder"
run_ssh_command 'mv -f /var/mobile/Media/1/files/FairPlay /var/mobile/Library/FairPlay'
run_ssh_command 'chmod 755 /var/mobile/Library/FairPlay'

log "Setting up activation records"
INTERNAL=$(run_ssh_command 'find /private/var/containers/Data/System -name internal')
ACTIVATION_RECORDS=$(run_ssh_command 'find /private/var/containers/Data/System -name activation_records')
ACTIVATION_RECORDS=${INTERNAL%?????????????????}
records=$ACTIVATION_RECORDS/Library/activation_records

run_ssh_command "mkdir $records"
run_ssh_command "mv -f /var/mobile/Media/1/files/activation_record.plist $records/activation_record.plist"
run_ssh_command "chmod 755 $records/activation_record.plist"
run_ssh_command "chflags uchg $records/activation_record.plist"
run_ssh_command "chflags nouchg /var/wireless/Library/Preferences/com.apple.commcenter.device_specific_nobackup.plist"
run_ssh_command "mv -f /var/mobile/Media/1/files/com.apple.commcenter.device_specific_nobackup.plist /var/wireless/Library/Preferences/com.apple.commcenter.device_specific_nobackup.plist"
run_ssh_command "chown root:mobile /var/wireless/Library/Preferences/com.apple.commcenter.device_specific_nobackup.plist"

log "Reloading mobileactivationd"
run_ssh_command "launchctl unload /System/Library/LaunchDaemons/com.apple.mobileactivationd.plist"
run_ssh_command "launchctl load /System/Library/LaunchDaemons/com.apple.mobileactivationd.plist"

log "Rebooting"
run_ssh_command '/sbin/reboot'

log "Activation files restored!"
