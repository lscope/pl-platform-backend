from setuptools import find_packages, setup



# Funzione per leggere i requisiti da requirements.txt
def read_requirements() -> list:
    """
    Read the requirements from the requirements.txt file and return them as a list.

    Returns:
        list: A list of requirements.
    """
    requirements = []

    with open("requirements.txt") as req:
        requirements.extend(req.read().splitlines())

    return requirements


setup(
    name="my_python_package",
    description="",
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    install_requires=read_requirements(),
    author="",
    author_email="",
    url="",
    license="MIT",
    python_requires=">=3.11",
)