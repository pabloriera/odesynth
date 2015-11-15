#! /bin/bash

# gcc -c $1.c -std=c99 -o $1.o -fPIC
# ld -export_dynamic -shared -o $1.pd_linux $1.o -lc -lm

gcc -c $1.c -o $1.o -Ofast
gcc -fpic -shared $1.o -o lib$1.so -Ofast
