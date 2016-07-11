HomeArchivingManager (ham.py)

A script to help reducing the backup requirements of collections of files by
burning selected files to CD/DVD/BluRay.

HAM works similar to a differential Backup. With a differential backup you
backup all files first. In the next backup only the files that have changed
or have been added get backuped.

For HAM the archived files get moved to a different location and a symlink to
them remains in place. Burn the files from the archived location and you do not
need to backup them anymore.
