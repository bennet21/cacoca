from pathlib import Path

from cacoca_posted_coupling import generate_cacoca_input
import logging

logging.basicConfig(level=logging.INFO)

code_folder = Path.cwd().parent
target_folder = code_folder / "cacoca" / "data" / "tech" / "posted"
posted_datafolder = code_folder / "posted" / "inst" / "extdata" / "database" / "tedfs" / "Tech"

posted_technames = ["Hydrogen Liquefaction"]
generate_cacoca_input(target_folder, posted_technames=posted_technames)

# generate_cacoca_input(target_folder, posted_datafolder=posted_datafolder)