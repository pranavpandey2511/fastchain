from setuptools import find_packages, setup

with open("README.md", "r") as f:
    project_description = f.read()


setup(
    name="fastchain",
    version="0.1.0",
    author="Pranav Pandey",
    author_email="pranavpandey2511@gmail.com",
    description="Fastest way to create LLM powered apps",
    long_description=project_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pranavpandey2511/fastchain",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    py_modules=[
        "langchain>=0.0.239",
        # vector dbs
        "vectordb",
        "qdrant-client==1.3.1",
        "weaviate-client==3.2.1",
        "chromadb>=0.4.2",
        # Data Sources
        "playwright==1.36.0",
        "PyMuPDF",
        "youtube-transcript-api",
        "beautifulsoup4",
        "pypdf",
        "pytube",
        "lxml",
        # Embeddings
        "openai",
        "sentence_transformers",
        "transformers",
        "gpt4all",
        "docx2txt",
        "pydantic==1.10.11",
        "duckduckgo-search",
        "requests",
    ],
    python_requires=">=3.9",
    install_require=["langchain >= 0.0.221"],
    extra_requires={"dev": ["pytest>=7.0", "twine>=4.0.2"]},
    license="MIT",
)
