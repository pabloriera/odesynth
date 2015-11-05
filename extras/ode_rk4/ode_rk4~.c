#include "m_pd.h"
#include "math.h"
#include "stdio.h"
#include <dlfcn.h>
#include <string.h>
#include <unistd.h>


//equation(t_sample X[], t_sample t, t_sample param[],t_sample dX[], t_sample input[] )
typedef  void (*equation_def)(t_sample X[], t_sample t, t_sample param[],t_sample dX[], t_sample input[] );


//CLASS INSTANCE
static t_class *ode_rk4_tilde_class;

//CLASS DEFINITION
typedef struct _ode_rk4_tilde {

  t_object obj;

  equation_def equation;

  int N_EQ, N_PARAMETERS, N_INPUTS, N_OUTPUTS;

  char libname[80];

  t_canvas *canvas;

  t_sample dt;
  t_sample t;
  t_sample fs;
  t_int flag;
  t_float f;

  //ARRAYS
  //N_EQ SIZE
  t_sample *setX;
  t_sample *x_prev;
  t_sample *F1, *F2, *F3, *F4, *xtemp;

  //N_PARAMETERS SIZE
  t_sample *params;

  //inlets & outlets
  t_sample **in;
  t_sample **out;

  //N_INPUTS SIZE
  t_sample *aux_in;


} t_ode_rk4_tilde;

//PERFORM FUNCTION
static t_int *ode_rk4_tilde_perform(t_int *w)
{

  t_ode_rk4_tilde *X = (t_ode_rk4_tilde *)(w[1]);

  int n = (int)(w[2]);

  t_sample dt = X->dt;

  t_sample t = X->t;

  t_sample *x = X->x_prev;

  if(X->flag)
  {
  	for(size_t i=0; i<X->N_EQ; i++ )
  		X->x_prev[i] = X->setX[i];

  	X->flag = 0;
  }

  t_sample f;

  for(size_t i=0; i<X->N_EQ; i++ )
  {
    f=x[i];
  	if (PD_BIGORSMALL(f))
		  x[i] = 0;         
  }


  //RK4
  t_sample half_dt = 0.5*dt;
  t_sample t_half = t + half_dt;
  t_sample t_full = t + dt;

  for (size_t k=0;k<n;k++)
  {
	
    	for(size_t i=0;i<X->N_INPUTS;i++)
            	X->aux_in[i]= X->in[i][k];
    		
    	//* Evaluate X->F1 = f(x,t).
    	X->equation( x, t, X->params, X->F1, X->aux_in );  

    	//* Evaluate X->F2 = f( x+tau*X->F1/2, t+tau/2 ).

    	for(size_t i=0; i<X->N_EQ; i++ )
    		X->xtemp[i] = x[i] + half_dt*X->F1[i];

    	X->equation( X->xtemp, t_half, X->params, X->F2, X->aux_in );  

    	//* Evaluate X->F3 = f( x+tau*X->F2/2, t+tau/2 ).
    	for(size_t i=0; i<X->N_EQ; i++ )
    		X->xtemp[i] = x[i] + half_dt*X->F2[i];

    	X->equation( X->xtemp, t_half, X->params, X->F3 , X->aux_in);

    	//* Evaluate X->F4 = f( x+tau*X->F3, t+tau ).
    	for(size_t i=0; i<X->N_EQ; i++ )
    		X->xtemp[i] = x[i] + dt*X->F3[i];

    	X->equation( X->xtemp, t_full, X->params, X->F4 , X->aux_in);

    	//* Return x(t+tau) computed from fourth-order R-K.
    	for(size_t i=0; i<X->N_EQ; i++ )
    	{
    		x[i] += dt/6.*(X->F1[i] + X->F4[i] + 2.*(X->F2[i]+X->F3[i]));
    		X->out[i][k] = x[i];	
    	}
									
  }

  X->t = t_full;

  return (w+3);
}

static void ode_rk4_tilde_dsp(t_ode_rk4_tilde *X, t_signal **sp)
{

  int n = 0;
  t_sample **dummy1= X->in;

  for(n=0;n<X->N_INPUTS;n++)
    *dummy1++=sp[n]->s_vec;

  t_sample **dummy2= X->out;

  for(n=X->N_INPUTS;n<X->N_INPUTS+X->N_OUTPUTS;n++)
    *dummy2++=sp[n]->s_vec;

  dsp_add(ode_rk4_tilde_perform, 2, X, sp[0]->s_n); //size of buffer

}

static void *ode_rk4_tilde_new(t_symbol *s, int argc, t_atom *argv)/* A_GIMME requiere de estos tres argumentos*/
{
  t_ode_rk4_tilde *X = (t_ode_rk4_tilde *)pd_new(ode_rk4_tilde_class);


  char cwd[1024];
  if (getcwd(cwd, sizeof(cwd)) != NULL)
    post("Current working dir: %s", cwd);
  else
    error("getcwd() error");

  if (argc!=2)
    error("1st arg is path, 2nd arg is library name");
  else
  {
    
    char *path = argv[0].a_w.w_symbol->s_name;
    char *name = argv[1].a_w.w_symbol->s_name;

    strcpy(X->libname, path);
    strcat(X->libname, "/lib");
    strcat(X->libname,name);
    strcat(X->libname,".so");

    X->canvas = canvas_getcurrent();

    char filnam[1000];
    char filename[1000];

    canvas_makefilename(X->canvas, X->libname, filnam, 1000);
    sys_bashfilename(filnam, filename);

    // post(path);
    // post(name);
    // post(X->libname);
    // post(filnam);
    post("Library file %s\n",filename);

    //dynamic shared lib
    void* handle = dlopen(filename, RTLD_LAZY);


    if(handle!=NULL)
    {

      //post("pointer adress %p",&X);
      //post("%s", X->libname);

      X->equation = ( equation_def ) dlsym(handle, "equation");

      int dims[4];

      void (*dimensions)(int*) ;
      dimensions = ( void (*)(int*) ) dlsym(handle, "dimensions");
      dimensions(dims);
      
      X->N_EQ = dims[0];
      X->N_PARAMETERS = dims[1];
      X->N_INPUTS = dims[2];
      X->N_OUTPUTS = dims[3];


      //N_EQ size alloc
      X->setX =  (t_sample *)getbytes( X->N_EQ * sizeof(t_sample) );
      X->x_prev =  (t_sample *)getbytes( X->N_EQ * sizeof(t_sample) );

      X->F1 = (t_sample *)getbytes( X->N_EQ * sizeof(t_sample) );
      X->F2 = (t_sample *)getbytes( X->N_EQ * sizeof(t_sample) );
      X->F3 = (t_sample *)getbytes( X->N_EQ * sizeof(t_sample) );
      X->F4 = (t_sample *)getbytes( X->N_EQ * sizeof(t_sample) );
      X->xtemp = (t_sample *)getbytes( X->N_EQ * sizeof(t_sample) );
      
      //X->N_INPUTS size alloc
      X->aux_in = (t_sample *)getbytes( X->N_INPUTS * sizeof(t_sample) );

      //PARAMS size alloc
      X->params =  (t_sample *)getbytes( X->N_PARAMETERS * sizeof(t_sample) );;

      //ARRAYS INLETS OUTLETS
      X->in = (t_sample **)getbytes(X->N_INPUTS * sizeof(t_sample *));
      X->out = (t_sample **)getbytes(X->N_OUTPUTS * sizeof(t_sample *));

      X->dt = 1.0/44100.0;
      for(size_t i=0; i<X->N_EQ; i++ )
      	X->x_prev[i] = 0.0;

      X->t  = 0;

      post("dt= %g", X->dt);
     
      //SIGNAL INLETS 
      for(size_t i=0;i<X->N_INPUTS-1;i++)
      	inlet_new(&X->obj, &X->obj.ob_pd, &s_signal, &s_signal);

      //SIGNAL OUTLETS 
      for(size_t i=0;i<X->N_OUTPUTS;i++)
      	outlet_new(&X->obj, &s_signal);

      
    
      

      return (void *)X;
    }
    else
    {
      error("libode.so not found");
    }

  }

}

static void ode_rk4_tilde_free(t_ode_rk4_tilde *X)
{
  freebytes(X->F1, X->N_EQ * sizeof(t_sample));
  freebytes(X->F2, X->N_EQ * sizeof(t_sample));
  freebytes(X->F3, X->N_EQ * sizeof(t_sample));
  freebytes(X->F4, X->N_EQ * sizeof(t_sample));

  freebytes(X->xtemp, X->N_EQ * sizeof(t_sample));
  freebytes(X->setX , X->N_EQ * sizeof(t_sample));
  freebytes(X->x_prev , X->N_EQ * sizeof(t_sample));
  
  freebytes(X->aux_in, X->N_INPUTS * sizeof(t_sample));
  freebytes(X->in, X->N_INPUTS * sizeof(t_sample* ));

  freebytes(X->out, X->N_OUTPUTS * sizeof(t_sample* ));

  freebytes(X->params, X->N_PARAMETERS * sizeof(t_sample));

  //dlclose(X->libname);
}


//DYN should have the number of arguments (A_DEFFLOAT) equal to X->N_EQ 
static void ode_rk4_tilde_setX(t_ode_rk4_tilde *X,t_floatarg x,t_floatarg y)
{
  X->setX[0] = x;
  X->setX[1] = y;
  X->flag = 1;       
}

static void ode_rk4_tilde_setP(t_ode_rk4_tilde *X, t_floatarg p, t_floatarg val)
{
	X->params[(int)p] = val;
}

void ode_rk4_tilde_setup(void) {

  ode_rk4_tilde_class = class_new(gensym("ode_rk4~"), (t_newmethod)ode_rk4_tilde_new, (t_method)ode_rk4_tilde_free,
   sizeof(t_ode_rk4_tilde), 0, A_GIMME, 0);

  //should have the number of arguments (A_DEFFLOAT) equal to N_EQ 
  class_addmethod(ode_rk4_tilde_class,(t_method)ode_rk4_tilde_setX, gensym("setX"),A_DEFFLOAT,A_DEFFLOAT,0);

  class_addmethod(ode_rk4_tilde_class,(t_method)ode_rk4_tilde_setP, gensym("setP"),A_DEFFLOAT,A_DEFFLOAT, 0);
  
  class_addmethod(ode_rk4_tilde_class, (t_method)ode_rk4_tilde_dsp, gensym("dsp"), 0);

  //CLASS_MAINSIGNALIN(ode_rk4_tilde_class, t_ode_rk4_tilde, f);
  class_addmethod(ode_rk4_tilde_class, nullfn, gensym("signal"), 0);
}

