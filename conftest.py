import os
import sys
from pathlib import Path

# Get absolute path to project root
project_root = Path(__file__).parent.absolute()
src_path = project_root / 'src'

# Add both paths
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path)) 