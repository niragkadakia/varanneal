"""
Example file for carrying out state and parameter estimation in the Lorenz 96
system using the weak-constrained variational method.

Varanneal implements the variational annealing algorithm and uses automatic
differentiation to do the action minimization at each step.

This scripts illustrates the use of time-dependent parameters
"""

import numpy as np
from varanneal import va_ode
import sys, time

# Define the model
def l96(t, x, p):
    k1 = p[:, 0]
    k2 = p[:, 1]
    state_vec = np.roll(x,1,1) * (np.roll(x,-1,1) - np.roll(x,2,1)) - x
    return (state_vec.T + k1 + 100*k2**2).T

D = 20

################################################################################
# Action/annealing parameters
################################################################################
# Measured variable indices
Lidx = np.arange(0, 20, 2)
# RM, RF0
RM = 1.0 / (0.5**2)
RF0 = 4.0e-6
# alpha, and beta ladder
alpha = 2
beta_array = np.linspace(0, 30, 31)

################################################################################
# Load observed data
################################################################################
# in this dataset, forcing switches from 8 to 15 at 2sec
data = np.load("l96_D20_dt0p025_N161_param=8,15.npy") 
times_data = data[:, 0]
#t0 = times_data[0]
#tf = times_data[-1]
dt_data = times_data[1] - times_data[0]
N_data = len(times_data)

data = data[:, 1:]
data = data[:, Lidx]

################################################################################
# Initial path/parameter guesses
################################################################################
# Same sampling rate for data and forward mapping
dt_model = dt_data
N_model = N_data
X0 = (20.0*np.random.rand(N_model * D) - 10.0).reshape((N_model, D))

# Sample forward mapping twice as f
#dt_model = dt_data / 2.0
#meas_nskip = 2
#N_model = (N_data - 1) * meas_nskip + 1
#X0 = (20.0*np.random.rand(N_model * D) - 10.0).reshape((N_model, D))

# Below lines are for initializing measured components to data; instead, we
# use the convenience option "init_to_data=True" in the anneal() function below.
#for i,l in enumerate(Lidx):
#    Xinit[:, l] = data[:, i]
#Xinit = Xinit.flatten()

# Parameters
Pidx = [0, 1]  # indices of estimated parameters
# Initial guess
P0 = np.random.uniform(0, 30, (N_model, 2)) # Time-dependent parameter

################################################################################
# Annealing
################################################################################
# Initialize Annealer
anneal1 = va_ode.Annealer()
# Set the Lorenz 96 model
anneal1.set_model(l96, D)
# Load the data into the Annealer object
anneal1.set_data(data, t=times_data)

state_bounds = [[-25, 25]]*D 
param_bounds = [[0, 30]]*2
bounds = state_bounds + param_bounds

# Run the annealing using L-BFGS-B
BFGS_options = {'gtol':1.0e-8, 'ftol':1.0e-8, 'maxfun':1000000, 'maxiter':1000000}
tstart = time.time()
anneal1.anneal(X0, P0, alpha, beta_array, RM, RF0, Lidx, Pidx, dt_model=dt_model,
               init_to_data=True, disc='SimpsonHermite', method='L-BFGS-B',
               opt_args=BFGS_options, bounds=bounds, adolcID=0)
print("\nADOL-C annealing completed in %f s."%(time.time() - tstart))

# Save the results of annealing
anneal1.save_paths("paths.npy")
anneal1.save_params("params.npy")
anneal1.save_action_errors("action_errors.npy")
