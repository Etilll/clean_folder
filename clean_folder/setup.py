from setuptools import setup, find_namespace_packages

setup(name='clean_folder',
      version='0.0.1',
      description='Sorts yer shite into nice folduhs',
      author='Etil',
      author_email='___',
      license='MIT',
      packages= find_namespace_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Windows",
        ],
      entry_points={'console_scripts': ['clean-folder = clean_folder.clean:packet_start']})