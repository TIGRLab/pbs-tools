#!/usr/bin/env python
"""
Takes a list of commands and makes a PBS submittable array job. 

Usage: $0 <cmds> <cmds-per-node> <output>

Arguments: 
    <cmds>             A file with commands to run, one per line.
    <cmds-per-node>    Number of commands to run in parallel per node. 
    <output>           Filename to output the script to.
"""
import sys
import os
import os.path
import math
import stat

NODES_PER_JOB=1     
CORES_PER_NODE=12
SCRIPT_TEMPLATE="""
#!/bin/bash
#PBS -l nodes=1:ppn={ppn}
#PBS -j oe
#PBS -V 
#PBS -t 1-{len}
cd ${{PBS_O_WORKDIR}}
sed -n $(( (${{PBS_ARRAYID}}-1)*{cpn}+1 )),$(( ${{PBS_ARRAYID}}*{cpn} ))p <<EOF | parallel -j{cpn}
{cmds}
EOF
""".lstrip()

def die(): 
    print __doc__
    sys.exit(1)

if __name__ == '__main__': 
    if len(sys.argv) < 3: die()

    _, cmd_file, cmds_per_node, output_file = sys.argv

    if not cmds_per_node.isdigit(): die
    if not os.path.exists(cmd_file): die()

    commands      = map(lambda x: x.strip(), open(cmd_file).readlines())
    cmds_per_node = int(cmds_per_node)
    array_len     = int(math.ceil(float(len(commands)) / cmds_per_node))

    script = SCRIPT_TEMPLATE.format(
        ppn  = CORES_PER_NODE,
        cpn  = cmds_per_node,
        cmds = "\n".join(commands),
        len  = array_len)

    output = open(output_file, 'w').write(script)
    os.chmod(output_file, stat.S_IRWXU)
