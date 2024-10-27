#!/usr/bin/env bash

# If config directory is empty, copy default configs
if [ -z "$(ls -A /app/config)" ]; then
    cp -f /app/default_config/* /app/config/ || echo "Warning: Could not copy default configs"
fi

# Start Streamlit
exec streamlit run main.py
