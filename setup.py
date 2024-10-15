import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="django-future-tasks",
    version=os.getenv("PACKAGE_VERSION", "1.3.0").replace("refs/tags/", ""),
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "croniter>=3.0.3,<3.1",
        "django-cronfield>=0.2.0,<0.3",
    ],
    license="MIT License",
    description="A library to create periodic, cron-like tasks or single tasks with a specified execution/start time and schedule it to run in the future.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/anexia/django-future-tasks",
    author="Armin Ster",
    author_email="aster@anexia-it.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
