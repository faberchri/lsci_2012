#! /usr/bin/env python

import os
import logging
import shutil
import subprocess
import re
import time


import numpy as np

from gc3libs.optimizer.dif_evolution import DifferentialEvolutionParallel

PENALTY_VALUE=100
run_counter=1

class nlcOne4eachPair():
  def __init__(self, lower_bds, upper_bds):

    self.lower_bds = lower_bds
    self.upper_bds = upper_bds
    self.ctryPair = ['JP', 'US']
 
    self.EY = [ 1.005416, 1.007292 ]
    self.sigmaY = [ 0.010643, 0.00862 ]
      
  def __call__(self, x):
    """
    Evaluates constraints. 
    Inputs: 
      x -- Habit parametrization, EH, sigmaH
    Outputs: 
      c -- Vector of constraints values, where c_i >= 0 indicates that constraint is satisified.
           Constraints 1-4 are bound constraints for EH and sigmaH
           Constraints 5 and 6 are economic constraints, one for Japan, one for US. 
    """
    c = np.array([])
    # bound constraints
    # EH box
    c = np.append(c, x[0] - self.lower_bds[0])
    c = np.append(c, -(x[0] - self.upper_bds[0]))
    # sigmaH box
    c = np.append(c, x[1] - self.lower_bds[1])
    c = np.append(c, -(x[1] - self.upper_bds[1]))
    # both countries have the same E
    EH     = np.array([x[0], x[0]])
    sigmaH = np.array([x[1], x[1]])

    for ixCtry in range(2):
      c = np.append(c, ( EH[ixCtry] / sigmaH[ixCtry] ) * ( self.sigmaY[ixCtry] / self.EY[ixCtry] ) - 1 )

    return c

def forwardPremium(vectors):
    """
    For each element of the input vectors, 'forwardPremiumOut'
    execution needs to be launched and supervised.
    Parameter file 'parameters.in' needs to be customised for each
    member of the given population and passed as part of the
    'forwardPremiumOut' execution either to the cloud or to the grid
    infrastructure.
    Once the execution of 'forwardPremiumOut' has terminated, the
    value of 'FamaFrenchbeta' should be extracted from the output file
    'simulation.out' located in the output folder.
    If a simulation does not produce a valid output, a penalty value
    should be used instead (use PENALTY_VALUE).
    The forwardPremium function terminates when *all* members of the
    given population have been evaluated and a result vector
    containing the scaled 'FamaFrenchbeta' values should then be returned

    Arguments:
    'vectors': list of population members to be exaluated
    example of vectors [ EX, sigmaX ] of size 10:
    
    [ 0.82679479,  0.00203506]
    [ 0.97514143,  0.00533972]
    [ 0.93623727,  0.00291099]
    [ 0.68093853,  0.00131595]
    [ 0.92752913,  0.00691528]
    [ 0.8828415,  0.00598679]
    [ 0.69607706,  0.00264031]
    [ 0.87176971,  0.00162624]
    [ 0.50521085,  0.00167101]
    [ 0.96557172,  0.00473888]

    Starting from 'parameters.in' template file
    http://ocikbapps.uzh.ch/gc3wiki/teaching/lsci2012/project/parameters.in
    substitute EA/EB and sigmaA/sigmaB from each
    member of the given population.

    Output:
    'results': list of corresponding 'FamaFrenchbeta' values scaled in respect
    of the empirical value ( -0.63 )
    Note: the FamaFrenchbeta value extracted from the simulation output file,
    needs to be compared with the empirical value and scaled in respect of the
    standard deviation:
            abs('FamaFrenchbeta' - (-0.63))/0.25
    This is the value that should be returned as part of 'results' for each element
    of the given population (i.e. vectors)

    """
    # replace this with a real implementation
    results = []
    print ("vecors")
    print vectors
    print ("---------------")
    
	# init run folder
    global run_counter
    run_folder = '/home/result/'+str(run_counter)

    successful_qsub_re = re.compile(r'Your job (\d+) \(".*"\) has been submitted')
    qstat_job_line_re = re.compile(r'^ *(\d+) +')

    # init all jobs
    jobs = { }
    counter = 0
    run_folder = '/home/results/'+str(run_counter)
    for ex, sigmax in vectors:
      qsub_output = subprocess.check_output(['qsub', '-b', 'y', '/home/worker/worker.sh', str(ex), str(sigmax), str(run_counter), str(counter)])
      match = successful_qsub_re.match(qsub_output)
      if match:
        jobid = match.group(1) # first parenthesized expression
        jobs[counter] = jobid
        logging.info("Job ex='%s', sigmax='%s' submitted as job %s", str(ex), str(sigmax), jobid)      
        print "Job ex='%s', sigmax='%s' submitted as job %s" % (str(ex), str(sigmax), jobid)
      
      counter = counter + 1

    # wait for all jobs to finish
    interval = 60
    jobids = jobs.values()
    while jobids:
      qstat_output = subprocess.check_output(['qstat'])
      running = set()
      for line in qstat_output.split('\n'):
        match = qstat_job_line_re.match(line)
        if match:
          jobid = match.group(1)
          if jobid in jobids:
            running.add(jobid)
      for jobid in set(jobids):
        if jobid not in running:
          jobids.remove(jobid)
          logging.info("Job %s finished.", jobid)
          print "Job %s finished." % jobid
      logging.info("waiting for jobs to finish")
      print "waiting for jobs to finish"
      time.sleep(interval)    

    # gather all parameters from output files
    result_counter = 0
    for ex, sigmax in vectors:
	  logging.info("getting results from session " + str(result_counter))
	  print "getting results from session " + str(result_counter)
	  FF_BETA = extractFFBeta(result_counter, run_folder)
	  logging.info("results received: "+str(FF_BETA))
	  print "results received: "+str(FF_BETA)
	  results.append(abs(FF_BETA - (-0.63))/0.25)
	  result_counter = result_counter + 1


    # increase run counter
    run_counter = run_counter + 1

    return results

def extractFFBeta(sessionId, rootDir):
    simuRes = rootDir + "/" + str(sessionId) + "/output/simulation.out"
    print "FF-Beta is extracted from: " + simuRes
    if (not os.path.isfile(simuRes)):
        # simulation did not converge result just some big value that will be discarded
        return 3.0
    for line in open(simuRes).readlines():
        if line.startswith("FamaFrenchBeta:"):
            name, value = line.split()
            return float(value)

def calibrate_forwardPremium():
  """
  Drver script to calibrate forwardPremium EX and sigmaX parameters.
  It uses DifferentialEvolutionParallel as an implementation of
  Ken Price's differential evolution
  algorithm: [[http://www1.icsi.berkeley.edu/~storn/code.html]].
  """

  dim = 2 # the population will be composed of 2 parameters to  optimze: [ EX, sigmaX ]
  lower_bounds = [0.5,0.001] # Respectivaly for [ EX, sigmaX ]
  upper_bounds = [1,0.01]  # Respectivaly for [ EX, sigmaX ]
  y_conv_crit = 2 # convergence treshold; stop when the evaluated output function y_conv_crit

  # define constraints
  ev_constr = nlcOne4eachPair(lower_bounds, upper_bounds)

  opt = DifferentialEvolutionParallel(
    dim = dim,          # number of parameters of the objective function
    lower_bds = lower_bounds,
    upper_bds = upper_bounds,
    pop_size = 10,     # number of population members
    de_step_size = 0.85,# DE-stepsize ex [0, 2]
    prob_crossover = 1, # crossover probabililty constant ex [0, 1]
    itermax = 200,      # maximum number of iterations (generations)
    x_conv_crit = None, # stop when variation among x's is < this
    y_conv_crit = y_conv_crit, # stop when ofunc < y_conv_crit
    de_strategy = 'DE_local_to_best',
    nlc = ev_constr # pass constraints object 
    )

  # Initialise population using the arguments passed to the
  # DifferentialEvolutionParallel iniitalization
  opt.new_pop = opt.draw_initial_sample()
  print("opt.new_pop: ")
  print(opt.new_pop)
  print ("---------------")

  # This is where the population gets evaluated
  # it is part of the initialization step
  newVals = forwardPremium(opt.new_pop)
  print("newVals: ")
  print(newVals)
  print ("---------------")
    
  # Update iteration count
  opt.cur_iter += 1

  # Update population and evaluate convergence
  opt.update_population(opt.new_pop, newVals)
    
    
    
  
  # !!!!!!!!!!!! Add 'not' !!!!!!!!!!!!!!!!!!! 
  while not opt.has_converged():
  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
      
      
      
      

    # Generate new population and enforce constrains
    opt.new_pop = opt.enforce_constr_re_evolve(opt.modify(opt.pop))

    # Update iteration count
    opt.cur_iter += 1

    # This is where the population gets evaluated
    # this step gets iterated until a population converges
    newVals = forwardPremium(opt.new_pop)

    # Update population and evaluate convergence
    opt.update_population(opt.new_pop, newVals)               

  # Once iteration has terminated, extract 'bestval' which should represent
  # the element in *all* populations that lead to the closest match to the
  # empirical value
  EX_best, sigmaX_best = opt.best

  print "Calibration converged after [%d] steps. EX_best: %f, sigmaX_best: %f" % (opt.cur_iter, EX_best, sigmaX_best)
  
  # write result fiel
  result_file = open('/root/result', 'w')
  result_file.write("Calibration converged after [%d] steps. EX_best: %f, sigmaX_best: %f" % (opt.cur_iter, EX_best, sigmaX_best))
  result_file.close()
  
if __name__ == '__main__':
  calibrate_forwardPremium()
