# Make sure to set a dict variable called headers

import platform


headers = {
    "program": "python",
    "version": platform.python_version(),
    "node": platform.node(),
    "environment": "test",
}
