#!/bin/bash

rm -rf ~/workspace/hpx/spack-*
rm -rf ~/workspace/LC/spack-*
spack uninstall --dependents lci
spack install
