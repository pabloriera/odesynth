# -*- coding: utf-8 -*-
path = 'ode_libs/'


def build(NAME):
    import subprocess,os

    print './'+path+'build_lib.sh',NAME
    os.chdir(path)
    subprocess.call(['./build_lib.sh',NAME])
    os.chdir("../")
    #os.system('./build.sh '+NAME+'~')       

def parse(NAME,VARIABLES,PARAMETROS,FORMULA,INPUTS):

    import re, os
#    math_functions = ['acos','asin','atan','atan2','floor','cos','cosh','exp','fabs','ceil','fmod','frexp','ldexp','log','log10','modf','pow','sin','sinh','sqrt','tan','tanh']
    
    
    try:    
        os.remove(path+NAME+".o")
        os.remove(path+NAME+".c")
    except:
        print 'New ode'
    
    eq = FORMULA
    dynvars = VARIABLES.split(" ")
    params = PARAMETROS.split(" ")
    
    if INPUTS.count(" ")==len(INPUTS):
        inputs = []
    else:
        inputs = INPUTS.split(" ")
    
    
    for p,i in zip(params,range(len(params))):
        eq = re.sub('\\b'+ p + '\\b', "param["+`i`+"]", eq)
    
    for p,i in zip(inputs,range(len(inputs))):
            eq = re.sub('\\b'+ p + '\\b', "input["+`i`+"]", eq)
    
    for dv,i in zip(dynvars,range(len(dynvars))):
        eq = re.sub('\\b'+ dv + '\\b', "X["+`i`+"]", eq)
    
    for dv,i in zip(dynvars,range(len(dynvars))):
        eq = re.sub('\\bd'+ dv + '\\b', "dX["+`i`+"]", eq)
        
    for dv,i in zip(dynvars,range(len(dynvars))):
        eq = eq.replace(';',';\n ')
    
    filename_in = "templates/ode_template.c"
    filename_out = path+NAME+".c"
    
    N_INPUTS = len(inputs)
    N_EQ = len(dynvars)
    N_OUTPUTS = N_EQ
    N_PARAMETERS = len(params)
    N_SIGNALS = N_INPUTS + N_OUTPUTS
    
    search = {}
    replace = {}
    search[0] = "//DYN0"
    replace[0] = "#define N_EQ "+ `N_EQ` + "\n#define N_OUTPUTS " + `N_OUTPUTS` + "\n#define N_INPUTS "+ `N_INPUTS` + "\n#define N_PARAMETERS "+ `N_PARAMETERS` + "\n"
    search[1] = "//DYN1"
    replace[1] = eq
            
    f1 = open(filename_in, 'r')
    f2 = open(filename_out, 'w')
    
    for line in f1:
        
        for k in search.keys():
            if search[k] in line:
                line = line.replace(search[k],replace[k])
        
        f2.write(line)
            
    f1.close()
    f2.close()


def patch(NAME,PARAMETROS,INPUTS,VARIABLES):

    outputs = VARIABLES.split(" ")
    params = PARAMETROS.split(" ")
    inputs = INPUTS.split(" ")

    params2 = [NAME+"/"+k for k in params]
    params2 = " ".join(params2)+";"

    f1 = open('templates/ode_system_template.pd', 'r')
    f2 = open(path+"ode_"+NAME+'.pd', 'w')

    for line in f1:
        lines = line.replace('NAME',NAME)
        lines = lines.replace('PARAMETERS',params2)
        lines = lines.replace('N_INPUTS',str(len(inputs)))
        lines = lines.replace('N_OUTPUTS',str(len(outputs)))
        f2.write(lines)

    f1.close()
    f2.close()

    print "Patch:", path+"ode_"+NAME+'.pd'
