#!/bin/bash

DIALER_NAME=$1

# Paths
PACKAGE_SETTINGS_PATH=$(python -c "import dialer; import os; print(os.path.join(os.path.dirname(dialer.__file__), 'configs', 'settings.py'))")
PACKAGE_DB_CONFIGS_PATH=$(python -c "import dialer; import os; print(os.path.join(os.path.dirname(dialer.__file__), 'database', 'database.sample.ini'))")
LOCAL_SETTINGS_PATH=$(pwd)/settings.py
LOCAL_DB_CONFIGS_PATH=$(pwd)/database/database.ini

# Copy settings.py to current directory
if [ ! -f "$LOCAL_SETTINGS_PATH" ]; then
  cp "$PACKAGE_SETTINGS_PATH" "$LOCAL_SETTINGS_PATH"
fi

# Create symlink to settings module
ln -sf "$PACKAGE_SETTINGS_PATH" "$LOCAL_SETTINGS_PATH"

# Copy database.ini to current directory
if [ ! -f "$LOCAL_DB_CONFIGS_PATH" ]; then
  mkdir $(pwd)/database
  cp "$PACKAGE_DB_CONFIGS_PATH" "$LOCAL_DB_CONFIGS_PATH"
fi

# Install cron jobs
(crontab -l ; echo "#Training AutoDialer calling and DB updating scripts for $DIALER_NAME Dialer") | crontab -
(crontab -l ; echo "0 7-21 * * * cd $(pwd) && run_dialer --call $DIALER_NAME") | crontab -
(crontab -l ; echo "0 22 * * * cd $(pwd) && run_dialer $DIALER_NAME && mv $(pwd)/logs/asterisk_$DIALER_NAME.log $(pwd)/logs/asterisk_$DIALER_NAME.log.bak && > $(pwd)/logs/asterisk_$DIALER_NAME.log") | crontab -

echo "Post-installation setup tasks completed."
