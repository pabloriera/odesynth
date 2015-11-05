#! /bin/bash
gcc -c $1.c -std=c99 -o $1.o -fPIC
ld -export_dynamic -shared -o $1.pd_linux $1.o -lc -lm

