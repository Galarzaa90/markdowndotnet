import yaml
from distutils import dir_util, file_util

# Copy generated files in output to docs
dir_util.copy_tree("output", "docs")

# Append generated index to mkdocs file
with open("_mkdocs.yml", "r") as f:
    config = yaml.load(f)  # Original mkdocs config

with open("docs/index.yml", 'r') as f:
    new_pages = yaml.load(f)

config["pages"].extend(new_pages)

with open("mkdocs.yml", "w") as f:
    yaml.dump(config, f, default_flow_style=False)

