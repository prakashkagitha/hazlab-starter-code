# hazlab-starter-code
Sample data and code for using solver and VAL in a typical LLM-as-formalizer paradigm

## Installing libraries
* Install python library: 
```pip install planutils```
* Install solver: 
```planutils install -y dual-bfws-ffparser```
* Install val: 
```planutils install -y val```
* For the next step to work you typically need apptainer in your system but apptainer is installed server wide at /usr/bin/apptainer (no need to install, but in case you run into problems)

## Running solver and VAL on command line

* Use solver with domain and problem files: 

```
planutils run dual-bfws-ffparser data/textual_blocksworld/BlocksWorld-100_PDDL/domain.pddl data/textual_blocksworld/BlocksWorld-100_PDDL/p02.pddl
```
This will output the error into console and if plan is found, saves it to file “plan” to the current directory. (wasn’t able to figure out how to set output plan file path)

* Use val with ground truth domain file, problem file, & plan: 
```
planutils run val Validate data/textual_blocksworld/BlocksWorld-100_PDDL/domain.pddl data/textual_blocksworld/BlocksWorld-100_PDDL/p02.pddl plan
```

There are some caveats with using this solver and val. For some problems, solver doesn't terminate so our programs run indefinetely. To solve this, the python code below uses timeouts, typically for 5 seconds.

The version of val in planutils does the job of validation but doesn't provide plan repair advice similar to VAL from KCL-Planning github repository. (check Cassie git repo for instructions on that: https://github.com/CassieHuang22/llm-as-pddl-formalizer)

## Running solver and VAL in python

The python file formalizer_check.py has the functionality of using the solver with timeout and val. The following example uses solver & val against ground truth domain and problem files. You could use ```run_solver``` or ```run_val``` independently in your code.

Note: This offline solver results in null plan for groud truth domain.pddl and p01.pddl. (There are some differences between offline solver and online solver. FYI!)

Command:
```
python formalizer_check.py     data/textual_blocksworld/BlocksWorld-100_PDDL/domain.pddl     data/textual_blocksworld/BlocksWorld-100_PDDL/p02.pddl
```

Output:

```
── SOLVER LOG ────────────────────────────────────────────────
 --- OK.
 Match tree built with 264 nodes.

PDDL problem description loaded: 
        Domain: BLOCKSWORLD
        Problem: BLOCKSWORLD-P02
        #Actions: 264
        #Fluents: 155
Goals found: 11
Goals_Edges found: 11
Starting search with 1-BFWS...
--[8 / 0]--
--[8 / 2]--
--[7 / 0]--
--[7 / 5]--
--[6 / 0]--
--[6 / 5]--
--[5 / 0]--
--[5 / 5]--
--[4 / 0]--
--[4 / 4]--
--[3 / 0]--
--[3 / 5]--
--[2 / 0]--
--[2 / 5]--
--[1 / 0]--
--[1 / 4]--
--[1 / 5]--
--[1 / 6]--
--[1 / 7]--
--[1 / 8]--
--[0 / 0]--
--[0 / 5]--
Total time: 0.001712
Nodes generated during search: 654
Nodes expanded during search: 317
Plan found with cost: 24
Fast-BFS search completed in 0.001712 secs
──────────────────────────────────────────────────────────────

── VAL LOG ───────────────────────────────────────────────────
Checking plan: plan_tmp.txt
Plan executed successfully - checking goal
Plan valid
Final value: 24 

Successful plans:
Value: 24
 plan_tmp.txt 24
──────────────────────────────────────────────────────────────

🎉  Plan is VALID.
```