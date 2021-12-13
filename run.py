#!/usr/bin/env python3

import os
from genkeycsr import app

#----------------------------------------
# launch
#----------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=True, 
        # configuration to run standalone with ssl
        #ssl_context=(
        #    '/etc/letsencrypt/archive/fully-qualified.domain.name/cert1.pem',
        #    '/etc/letsencrypt/archive/fully-qualified.domain.name/privkey1.pem'
        #)
    )
