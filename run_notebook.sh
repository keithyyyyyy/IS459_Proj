#!/bin/bash
jupyter nbconvert --to notebook --execute analysis.ipynb
sudo rm results.csv