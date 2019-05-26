# PYDROMMER: Mass IP port scanner
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
![Platform](https://img.shields.io/badge/platform-linux-green.svg)

Pydrommer is an simple asynchronous Internet-scale port scanner that uses asyncio. It's flexible, 
allowing arbitrary port, address ranges and other. There is also a module for receiving HTTP headers 
and detection jsonrpc.

##### Currently it supports the following modules:
  + ports_scanner           : Discovers open ports
  + http_headers_getter     : Gets HTTP headers or only discovers JSON RPC

**The following actions were performed on ubuntu 19.04 with
python3.7**

## Installing
```bash
git clone https://github.com/mkbeh/pydrommer
cd pydrommer
python3.7 setup.py install
pydrommer
```

## Usage
```
List of supported input:
  - hosts:
    * file/file with URLS
    * single IP
    * subnet
    * URL (only for http_headers_getter module)
    
  -ports:
    * range         : 0-65535
    * separated     : 80,8080,27017
    * combined      : 80,1000-2000,8080,10500,12000-13000
    * file          : with single ports
    * single port
---------------------------------------------------------------------------------------------------------
  IMPORTANT NOTE:
  
  In order to get HTTP headers or to detect a JSON-RPC for hosts from the final file that the src scanner 
  generates after scanning on open ports - use the following syntax:

  Ex.: src -iH ports_checker-final-24-05-19-21-34-03.prm -iP ports_checker-final-24-05-19-21-34-03.prm
  
  - In the example above the same file is specified.
  - *prm extension in file is required!
```

### Usage examples
```
# Will show available modules
pydrommer  

# Will show help message for module          
pydrommer <module_name>

# Will scan current IP by range.        
pydrommer ports_scanner -iH 192.0.2.1 -iP 1-65535

# Will parse HTTP headers for subnet by combined ports
pydrommer http_headers_getter -iH 192.0.2.1/30 -iP 1-1000,1253
```
