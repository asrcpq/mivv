import setuptools

setuptools.setup(
	name = "mivv",
	version = "0.1.0",
	packages = setuptools.find_packages(),
	entry_points = {
		"gui_scripts": ["mivv = mivv.__main__:main"],
	},
	python_requires = ">=3.6",
)
