#! /bin/bash
gcc -fpic -shared -ldl -lc -lm -std=c99 ode_rk4~.c -o ode_rk4~.pd_linux
