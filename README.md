# Python Finance Library

<table>
<tr>
  <td>Latest Release</td>
  <td><img src="https://img.shields.io/pypi/v/finance-python.svg" alt="latest release" /></td>
</tr>
<tr>
  <td>Build Status</td>
  <td>
    <a href="https://travis-ci.org/alpha-miner/Finance-Python">
    <img src="https://travis-ci.org/alpha-miner/Finance-Python.svg?branch=master" alt="travis build status" />
    </a>
  </td>
</tr>
<tr>
  <td>Coverage</td>
  <td><img src="https://coveralls.io/repos/alpha-miner/Finance-Python/badge.svg?branch=master&service=github" alt="coverage" /></td>
</tr>
</table>

A financial calculation library implemented in pure Python, with the goal of providing necessary tools for quantitative trading, including but not limited to: pricing analysis tools and technical analysis indicators. Some of the implementations refer to quantlib.
### TODO list

- [x] Add window functions based on event length (Count and CountUnique)
- [x] Add more functions based on time window length

### Dependencies

    coverage
    cython
    enum34
    numpy
    pandas
    scipy
    six
    
And related c/c++ compilers (such as gcc under Linux, visual studio under windows)

### Installation

1. Install from latest source code

    First save the code locally：
    
        git clone https://github.com/ruhoDev/Python-Finance-Library.git (github repository)
        cd finance-Python
       
    Just run the following command：
    
        python setpy.py install
    
    After installation, you can run the test directly：
    
        python PyFin/tests/testSuite.py
        
2. Install from ``pypi``
    
    Just run the following command：
    
        pip install Finance-Python
    
    
### Development Environment

In the code directory, you need to run the following command：

    python setup.py build_ext --inplace

### The main function

* An indicator library that can implement compound operations and can be easily combined with pandas;
* Calendar-based financial date calculations, including holiday arrangements in different markets;
* Portfolio optimization function (experimental stage, limited functionality and may be significantly modified in the future);
* Pricing models for some financial products (limited functionality).
