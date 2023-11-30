import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="django-future-tasks",
    version=os.getenv("PACKAGE_VERSION", "1.1.0").replace("refs/tags/", ""),
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "croniter>=1.4.1,<1.5",
        "cron-descriptor>=1.4.0,<1.5",
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
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
