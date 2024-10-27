#!/usr/bin/env bash

# If config directory is empty, copy default configs
if [ -z "$(ls -A /app/config)" ]; then
    cp /app/default_config/* /app/config/
fi

# Start Streamlit
streamlit run main.py
