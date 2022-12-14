import setuptools
from webhook_listener import version

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Webhook_Listener",
    version=version.__version__,
    author="Todd Roberts",
    author_email="todd@toddrob.com",
    description="Very basic webserver module to listen for webhooks and forward requests to predefined functions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/toddrob99/Webhooks",
    packages=setuptools.find_packages(),
    install_requires=['cherrypy'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
