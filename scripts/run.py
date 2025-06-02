import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import app

if __name__ == "__main__":
    app.mainloop() 