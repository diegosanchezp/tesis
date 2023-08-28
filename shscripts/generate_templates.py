import sys
from pathlib import Path
from dataclasses import dataclass
import logging

import environ
from jinja2 import Environment, FileSystemLoader, select_autoescape

BASE_DIR = Path(__file__).resolve().parent.parent  # The root of this repo

# Add the root dir so we can resolve imports
sys.path.append(str(BASE_DIR))

DOCKER_DIR = BASE_DIR / "docker" / "production"
NGINX_DIR = BASE_DIR / "nginx"

env = environ.Env()
MODE = env("MODE")
HOSTNAME = env("HOST_NAME")

logging.basicConfig(
    stream=sys.stdout,
    datefmt="%Y-%m-%d %H:%M:%S",
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)

jinja_env = Environment(
    loader=FileSystemLoader(BASE_DIR),
    autoescape=select_autoescape(),
    # Remove whitespace that is left behind by jinja syntax
    trim_blocks=True,
    lstrip_blocks=True,
)

context = {
    "production": MODE == "production",
    "production_test": MODE == "production_test",
    "hostname": HOSTNAME,
}


@dataclass
class TemplateFile:
    name: str
    out_name: str
    path: Path

    def get_template(self):
        return jinja_env.get_template(
            f"{self.path.parts[-1]}/{self.name}"
        )

    def save(self):
        template = self.get_template()
        rendered_template = template.render(**context)

        with open(NGINX_DIR / self.out_name, "w") as f:
            f.write(rendered_template)

        logging.info(msg=f"Saved template {self.out_name}")

if __name__ == "__main__":

    templates = [
        TemplateFile(path=NGINX_DIR, name="nginx_template.conf", out_name="nginx.conf"),
    ]


    for template in templates:
        # Save
        template.save()
