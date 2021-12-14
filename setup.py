import setuptools

setuptools.setup(
	name="mivv",
	version="0.1.0",
	package_dir={"": "mivv"},
	packages=setuptools.find_packages(where="mivv"),
	python_requires=">=3.6",
)
