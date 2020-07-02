#!/bin/bash
conan source . -sf src 
conan install . -if build --build missing
conan build . -bf build -sf src
conan export-pkg . IlmBase/2.4.0@rcldsl/stable -s build_type=Release -sf src -bf build --force