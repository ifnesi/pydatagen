# Make sure to set a global variable called "headers" (dict)

import platform


headers = {
    "program": "python",
    "version": platform.python_version(),
    "node": platform.node(),
    "environment": "test",
}
