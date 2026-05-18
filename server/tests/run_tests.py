import subprocess
from pathlib import Path

server_dir = Path(__file__).parent.parent

subprocess.run(f"""python -m pytest {Path(__file__).parent}/unit -q""", cwd=server_dir, shell=True)


