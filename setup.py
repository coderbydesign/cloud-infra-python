import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cloud-infra-python",
    version="0.0.1",
    author="Keith Walsh",
    author_email="kwalsh@redhat.com",
    description="A python client which provides an interface to cloud.redhat RBAC and entitlements infrastructure services.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RedHatInsights/cloud-infra-ruby",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
