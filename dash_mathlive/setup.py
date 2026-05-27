import json
from pathlib import Path

from setuptools import setup

here = Path(__file__).parent
with open(here / 'dash_mathlive' / 'package-info.json') as f:
    package = json.load(f)

package_name = package["name"].replace(" ", "_").replace("-", "_")

setup(
    name=package_name,
    version=package["version"],
    author=package['author'],
    packages=[package_name],
    include_package_data=True,
    package_data={
        package_name: ['*.js', '*.js.map', '*.json'],
    },
    license=package['license'],
    description=package.get('description', package_name),
    install_requires=[],
    classifiers=[
        'Framework :: Dash',
    ],
)
