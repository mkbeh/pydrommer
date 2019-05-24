

MODULES = """
-------------------------------------------------------------------------------------------------------
:::::::::  :::   ::: :::::::::  :::::::::   ::::::::  ::::    ::::  ::::    ::::  :::::::::: :::::::::  
:+:    :+: :+:   :+: :+:    :+: :+:    :+: :+:    :+: +:+:+: :+:+:+ +:+:+: :+:+:+ :+:        :+:    :+: 
+:+    +:+  +:+ +:+  +:+    +:+ +:+    +:+ +:+    +:+ +:+ +:+:+ +:+ +:+ +:+:+ +:+ +:+        +:+    +:+ 
+#++:++#+    +#++:   +#+    +:+ +#++:++#:  +#+    +:+ +#+  +:+  +#+ +#+  +:+  +#+ +#++:++#   +#++:++#:  
+#+           +#+    +#+    +#+ +#+    +#+ +#+    +#+ +#+       +#+ +#+       +#+ +#+        +#+    +#+ 
#+#           #+#    #+#    #+# #+#    #+# #+#    #+# #+#       #+# #+#       #+# #+#        #+#    #+# 
###           ###    #########  ###    ###  ########  ###       ### ###       ### ########## ###    ### 
-------------------------------------------------------------------------------------------------------
Pydrommer is an simple asynchronous Internet-scale port scanner that uses asyncio. It's flexible, 
allowing arbitrary port, address ranges and other. There is also a module for receiving HTTP headers 
and detection jsonrpc.
--------------------------------------------------------------------------------------------------------
Currently it supports the following modules:
  + ports_scanner           : Discovers open ports
  + http_headers_getter     : Gets HTTP headers or only discovers JSON RPC
--------------------------------------------------------------------------------------------------------
List of supported input:
  - hosts:
    * file
    * single IP
    * subnet
    * URL (only for http_headers_getter module)
    
  -ports:
    * range         : 0-65535
    * separated     : 80,8080,27017
    * combined      : 80,1000-2000,8080,10500,12000-13000
    * file          
    * single port
---------------------------------------------------------------------------------------------------------
  IMPORTANT NOTE:
  
  In order to get HTTP headers or to detect a JSON-RPC for hosts from the final file that the pydrommer scanner generates 
  after scanning on open ports - use the following syntax:

  Ex.: pydrommer -iH ports_checker-final-24-05-19-21-34-03.prm -iP ports_checker-final-24-05-19-21-34-03.prm

  *prm extension in file is required!
"""

CYCLE_TIMEOUT_HELP = 'Timeout between block cycles.'
READ_TIMEOUT_HELP = 'Time to wait for a response from the server after sending the request.'
OUTPUT_HELP = 'Where to record the result of the scan. By default in the file, ' \
              'which located by path -> ~/.local/share/pydrommer/'
HOSTS_BLOCK_SIZE_HELP = 'The number of hosts that will be processed simultaneously.'
PORTS_BLOCK_SIZE_HELP = 'The number of ports that will be processed simultaneously for each host.'
