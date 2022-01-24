import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="delivery_insights",
    version="0.0.1",
    author="Badr Arrabatchou",
    author_email="arr.badr@gmail.com",
    description=("Pipeline use case"),
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    long_description=read("README.md"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    entry_points={
        "console_scripts": [
            "delivery_insights=delivery_insights.main:main",
            "extract_pipeline=delivery_insights.pipelines.extract.pipeline:extract_pipeline",
            "transform_pipeline=delivery_insights.pipelines.transform.pipeline:transform_pipeline",
            "load_pipeline=delivery_insights.pipelines.load.pipeline:load_pipeline",
            "visualize_pipeline=delivery_insights.pipelines.visualize.pipeline:visualize_pipeline",
        ]
    },
)
