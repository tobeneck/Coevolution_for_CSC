# A Coevolution approach for the Multi-objective Circular Supply Chain Problem

This repository contains the code to generate the data for Paper "A Coevolution approach for the Multi-objective Circular Supply Chain Problem", which can be found [here on IEEE Xplore](https://ieeexplore.ieee.org/document/10195126).

## Running the Code

The tests were generated using python 3.9.6, the required packages can be found in "requirements.txt".
There was only one test run shown in the paper. The test can be generated using these two files:

```python
python3 -m venv venv
source venv/bin/activate
pip3 install requirements.txt
python3 generate_test.py
python3 visualize.py
```

## Citation

If you have used this research, you can cite it with:

T. Benecke, O. Antons, S. Mostaghim and J. Arlinghaus, "A Coevolution Approach for the Multi-objective Circular Supply Chain Problem," 2023 IEEE Conference on Artificial Intelligence (CAI), Santa Clara, CA, USA, 2023, pp. 222-223, [doi: 10.1109/CAI54212.2023.00103.](https://ieeexplore.ieee.org/document/10195126)

Bibtex:
```bibtex
@INPROCEEDINGS{coevolution_csc,
  author={Benecke, Tobias and Antons, Oliver and Mostaghim, Sanaz and Arlinghaus, Julia},
  booktitle={2023 IEEE Conference on Artificial Intelligence (CAI)}, 
  title={A Coevolution Approach for the Multi-objective Circular Supply Chain Problem}, 
  year={2023},
  doi={10.1109/CAI54212.2023.00103}
}
```
