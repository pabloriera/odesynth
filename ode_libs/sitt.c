#define PI 3.141592653589793238462

#include "m_pd.h"

#define N_EQ 2
#define N_OUTPUTS 2
#define N_INPUTS 1
#define N_PARAMETERS 3


void dimensions(int x[])
{
	x[0] = N_EQ;
	x[1] = N_PARAMETERS;
	x[2] = N_INPUTS;
	x[3] = N_OUTPUTS; 
}

void equation(t_sample X[], t_sample t, t_sample param[],t_sample dX[], t_sample input[] )
{
dX[0] = X[1];
 
  dX[1] = (param[0]*param[2]+param[1]*param[2]*X[0] + X[0]*X[0]*param[2]-X[0]*X[1]-X[0]*X[0]*X[0]-X[0]*X[0]*X[1])*param[2] + input[0];
 
  
}
