#!/bin/bash

ID="template@template.com"
PW="template_password"

# Mini 데이터셋 다운로드
python download_nuplan.py --username "$ID" --password "$PW" \
    --maps --log-db