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
    
    import StringIO
    
    outputs = VARIABLES.split(" ")
    params = PARAMETROS.split(" ")
    inputs = INPUTS.split(" ")

#    ['INPUTS',[['Osc','Freq'],['Osc','Amp'],['Noise','Fc'],['Noise','Amp'],['External','Input']]],['DELAY/FEEDBACK',[['Delay','Time'],['Feedback','Amp']]]

     
    f1 = open('templates/core_template.txt', 'r')
    ftmp = StringIO.StringIO()
    f2 = open(path+NAME+'.pd', 'w')

    for lines in f1:
        
        line = lines.replace('name',NAME)
        line = line.replace('f*OUTPUTS','f '*len(outputs))
        line = line.replace('\$1*OUTPUTS'," ".join(['\$'+str(i) for i in range(1,len(outputs)+1)]))
        ftmp.write(line)
    
    f1.close()    
    ftmp.seek(0)
    
    width = 800
    
    f2.write(ftmp.readline().replace('WW',str(width)))
        
    for i in range(25):
        f2.write(ftmp.readline())

    lines = ftmp.readline()
    for i in range(len(outputs)):
        f2.write(lines.replace('YY',str(i*15+280)).replace('id',str(i)))  
        
    sepx = 230    
#   INPUTS DYNAMIC 3  
    lines = {}
    lines[0] = ftmp.readline()
    lines[1] = ftmp.readline()
    lines[2] = ftmp.readline()
    
    for i in range(len(inputs)):
        for l in lines:
            f2.write(lines[l].replace('XX',str(i*sepx)).replace('id',str(i)))   
    
#   PARAMS DYNAMIC 4
    lines = {}    
    lines[0] = ftmp.readline()
    lines[1] = ftmp.readline()
    lines[2] = ftmp.readline()
    lines[3] = ftmp.readline()
        
    for i in range(len(params)):
        for l in lines:
            f2.write(lines[l].replace('XX',str(i*sepx)).replace('id',str(i)))

#   OUTPUTS DYNAMIC 4
    lines = {}
    
    lines[0] = ftmp.readline()
    lines[1] = ftmp.readline()
    lines[2] = ftmp.readline()
    lines[3] = ftmp.readline()
    
    for i in range(len(outputs)):
        for l in lines:
            f2.write(lines[l].replace('XX',str(i*sepx)).replace('id',str(i)))   
                
    f2.write(ftmp.readline())    
    
    sepx = 42

#   FADERS PARAMS DYNAMIC 6
    lines = {}
    
    for i in range(6):
        lines[i] = ftmp.readline()
 
    for i in range(len(params)): 
        for l in lines:
            f2.write(lines[l].replace('XX',str(i*sepx)).replace('id',str(i)).replace('paramtext',params[i]))
            
    width = 20+42*len(params)
    
    f2.write(ftmp.readline().replace('WW',str(width)))
    
    f1 = open('templates/connections_template.txt', 'r')    
    f2.write("".join(f1.readlines()))
        
    odeid= 16
    #INPUTS
    in_list = range(28,28+3*len(inputs))
    
    #PARAMS
    params_list = range(in_list[-1]+1,in_list[-1]+1+4*len(params))
    
    #OUTS
    out_list = range(params_list[-1]+1,params_list[-1]+1+4*len(outputs))
    
    for k,l in zip(range(len(inputs)),in_list[0:-1:3]):
        id0 = l; id1=l+1; c0 = 0;c1=0
        connect = "#X connect %d %d %d %d;\n" % (id0, c0, id1, c1)
        f2.write(connect)
        id0 = l+2; id1=odeid; c0 = 0;c1=k
        connect = "#X connect %d %d %d %d;\n" % (id0, c0, id1, c1)
        f2.write(connect)

    for k,l in zip(range(len(params)),params_list[0:-1:4]):
        id0 = l+1; id1=l+2; c0 = 0;c1=0
        connect = "#X connect %d %d %d %d;\n" % (id0, c0, id1, c1)
        f2.write(connect)
        id0 = l+2; id1=l+3; c0 = 0;c1=0
        connect = "#X connect %d %d %d %d;\n" % (id0, c0, id1, c1)
        f2.write(connect)

    for k,l in zip(range(len(out_list)),out_list[0:-1:4]):
        id0 = odeid; id1=l; c0 = k;c1=0
        connect = "#X connect %d %d %d %d;\n" % (id0, c0, id1, c1)
        f2.write(connect)
        id0 = odeid; id1=l+1; c0 = k;c1=0
        connect = "#X connect %d %d %d %d;\n" % (id0, c0, id1, c1)
        f2.write(connect)
        id0 = l+2; id1=l+3; c0 = 0;c1=0
        connect = "#X connect %d %d %d %d;\n" % (id0, c0, id1, c1)
        f2.write(connect)
    
        id0 = 25; id1=22; c0 = 0;c1=1
        connect = "#X connect %d %d %d %d;\n" % (id0, c0, id1, c1)
        f2.write(connect)  
        
    for i in range(len(outputs)-1):
        id0 = 25+i+1; id1=23; c0 = 0;c1=i+1
        connect = "#X connect %d %d %d %d;\n" % (id0, c0, id1, c1)
        f2.write(connect)
        

    f2.close()
    