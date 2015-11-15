
import pypdode

# #HOPF NORMAL FORM
# VARIABLES = "x y"
# PARAMETROS = "e w"
# INPUTS = "I1 I2"
# FORMULA = "dx = 2*PI*w*y + e*x - (x*x+y*y)*x + I1; dy = -2*PI*w*x + e*y - (x*x+y*y)*y + I2;"
# NAME = "hopf"

# odepd.parse(NAME,VARIABLES,PARAMETROS,FORMULA,INPUTS)
# odepd.build(NAME)
# odepd.patch(NAME,PARAMETROS,INPUTS,VARIABLES)

#LORENZ
VARIABLES = "x y z"
PARAMETROS = "r b tau"
INPUTS = "I1"

FORMULA = "dx = (11.0*(y - x)+I1)/tau;"+\
          "dy = (x*(r - z) - y)/tau;"+\
          "dz = (x*y - b*z)/tau;"

NAME = "LLorenz"

pypdode.parse(NAME,VARIABLES,PARAMETROS,FORMULA,INPUTS)
pypdode.build(NAME)
pypdode.patch(NAME,PARAMETROS,INPUTS,VARIABLES)
