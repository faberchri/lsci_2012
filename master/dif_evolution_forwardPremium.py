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
POPULATION_SIZE=100
LOG_FILE="/home/lsci/optimizer.log"
LOGGER="toBeInitialized"
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
    global LOGGER
    results = []
    LOGGER.info("Starting forwardPremium with population: " + ', '.join(map(str, vectors)) )
    
	# init run folder
    global run_counter
    run_folder = '/home/lsci/result/'+str(run_counter)

    successful_qsub_re = re.compile(r'Your job (\d+) \(".*"\) has been submitted')
    job_failure = re.compile(r'error: job id (\d+) not found')
    qstat_job_line_re = re.compile(r'^ *(\d+) +')

    # init all jobs
    jobs = { }
    counter = 0
    for ex, sigmax in vectors:
      qsub_output = subprocess.check_output(['qsub','-r','yes', '-b', 'y', '/home/lsci/worker/worker.sh', str(ex), str(sigmax), str(run_counter), str(counter)])
      match = successful_qsub_re.match(qsub_output)
      if match:
        jobid = match.group(1) # first parenthesized expression
        jobs[counter] = jobid
        LOGGER.info("Job ex='%s', sigmax='%s' submitted as job %s", str(ex), str(sigmax), jobid)
      
      counter = counter + 1

    # wait for all jobs to finish
    interval = 60
    jobids = jobs.values()
    max_waiting_time = 2280 # we dont't wait longer for a single cycle to complete than 38 minutes
    while jobids:
      qstat_output = subprocess.check_output(['qstat'])
      running = set()
      for line in qstat_output.split('\n'):
        match = qstat_job_line_re.match(line)
        if match:
          jobid = match.group(1)
          if jobid in jobids:
            running.add(jobid)
            # check if job failed
            # TODO
	
      for jobid in set(jobids):
        if jobid not in running:
          jobids.remove(jobid)
          LOGGER.info("Job %s finished.", jobid)
      LOGGER.info("waiting for jobs to finish")
      LOGGER.info("qstat output:\n" + subprocess.check_output(['qstat']))
      LOGGER.info("qhost output:\n" + subprocess.check_output(['qhost']))
      if max_waiting_time <= 0:
          #max waiting time is over, delete all submitted jobs
          LOGGER.info("Max wait time is over. All submitted and not yet finished jobs are deleted.")
          del_output=subprocess.check_output(['qdel','-u','*'])
          LOGGER.info("qdel output:\n" + del_output)
          LOGGER.info("qstat output after jobs deletion:\n" + subprocess.check_output(['qstat']))
          break 
          
      time.sleep(interval)    
      max_waiting_time = max_waiting_time - interval
      
    # gather all parameters from output files
    result_counter = 0
    for ex, sigmax in vectors:
	  LOGGER.info("getting results from session " + str(result_counter))
	  FF_BETA = extractFFBeta(result_counter, run_folder)
	  LOGGER.info("results received: "+str(FF_BETA))
	  results.append(abs(FF_BETA - (-0.63))/0.25)
	  result_counter = result_counter + 1
   
    global POPULATION_SIZE
    while len(results) < POPULATION_SIZE:
        global PENALTY_VALUE
        LOGGER.info("Additional penalty value is added because results vector is smaller than POPULATION_SIZE: len(results) = " +str(len(results)) + ";  POPULATION_SIZE: " + str(POPULATION_SIZE))
        results.append(PENALTY_VALUE)
    
    LOGGER.info("Results of forwardPremium (FF-Betas) of iteration " +str(run_counter) + ": " + ', '.join(map(str, results)))
    # increase run counter
    run_counter = run_counter + 1
    return results

def extractFFBeta(sessionId, rootDir):
    simuRes = rootDir + "/" + str(sessionId) + "/output/simulation.out"
    if (not os.path.isfile(simuRes)):
        # simulation did not converge result just some big value that will be discarded
        global PENALTY_VALUE
        return PENALTY_VALUE
    for line in open(simuRes).readlines():
        if line.startswith("FamaFrenchBeta:"):
            name, value = line.split()
            return float(value)
            
def initLogging():
  # Set up logger
  log = logging.getLogger('gc3.gc3libs.EvolutionaryAlgorithm')
  log.setLevel(logging.DEBUG)
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # logging.basicConfig(filename=LOG_FILE,level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
  log.propagate = 0
  stream_handler = logging.StreamHandler()
  stream_handler.setFormatter(formatter)
  stream_handler.setLevel(logging.DEBUG)
  import gc3libs
  global LOG_FILE
  file_handler = logging.FileHandler(LOG_FILE, mode = 'w')
  file_handler.setLevel(logging.DEBUG)
  file_handler.setFormatter(formatter)
  log.addHandler(stream_handler)
  log.addHandler(file_handler)
  global LOGGER
  LOGGER = log

def calibrate_forwardPremium():
  """
  Drver script to calibrate forwardPremium EX and sigmaX parameters.
  It uses DifferentialEvolutionParallel as an implementation of
  Ken Price's differential evolution
  algorithm: [[http://www1.icsi.berkeley.edu/~storn/code.html]].
  """
  global LOGGER
  dim = 2 # the population will be composed of 2 parameters to  optimze: [ EX, sigmaX ]
  lower_bounds = [0.5,0.001] # Respectivaly for [ EX, sigmaX ]
  upper_bounds = [1,0.01]  # Respectivaly for [ EX, sigmaX ]
  y_conv_crit = 0.98 # convergence treshold; stop when the evaluated output function y_conv_crit

  # define constraints
  ev_constr = nlcOne4eachPair(lower_bounds, upper_bounds)
  
  global POPULATION_SIZE
  opt = DifferentialEvolutionParallel(
    dim = dim,          # number of parameters of the objective function
    lower_bds = lower_bounds,
    upper_bds = upper_bounds,
    pop_size = POPULATION_SIZE,     # number of population members
    de_step_size = 0.85,# DE-stepsize ex [0, 2]
    prob_crossover = 1, # crossover probabililty constant ex [0, 1]
    itermax = 20,      # maximum number of iterations (generations)
    x_conv_crit = None, # stop when variation among x's is < this
    y_conv_crit = y_conv_crit, # stop when ofunc < y_conv_crit
    de_strategy = 'DE_local_to_best',
    nlc = ev_constr # pass constraints object 
    )

  # Initialise population using the arguments passed to the
  # DifferentialEvolutionParallel iniitalization
  opt.new_pop = opt.draw_initial_sample()
  LOGGER.info("Initial sample drawn: " + ', '.join(map(str, opt.new_pop)) )
  
  # This is where the population gets evaluated
  # it is part of the initialization step
  newVals = forwardPremium(opt.new_pop)
    
  # Update iteration count
  opt.cur_iter += 1

  # Update population and evaluate convergence
  opt.update_population(opt.new_pop, newVals)
    
  while not opt.has_converged():
    LOGGER.info("*********************************************************************")
    LOGGER.info("Optimization has not converged after performing iteration [" + str(opt.cur_iter) + "].")  
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

  LOGGER.info("Optimization converged after [%d] steps. EX_best: %f, sigmaX_best: %f" % (opt.cur_iter, EX_best, sigmaX_best))
  
  # write result fiel
  result_file = open('/home/lsci/result_output', 'w')
  result_file.write("Optimization converged after [%d] steps. EX_best: %f, sigmaX_best: %f" % (opt.cur_iter, EX_best, sigmaX_best))
  result_file.close()

  
if __name__ == '__main__':
  initLogging()
  calibrate_forwardPremium()
