#!/usr/bin/env python3.9

import os
from gen_keycsr import app

#----------------------------------------
# launch
#----------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=True, 
        ssl_context=(
            '/etc/apache2/ssl/cert.pem',
            '/etc/apache2/ssl/key.pem'
        )
    )
