@echo off
title Web App Assistant
@echo Starting Web App Assistant
http-server -p 8082 -S -C .\cert.pem -K .\key.pem