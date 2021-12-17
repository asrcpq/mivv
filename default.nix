with import <nixpkgs>{};

python3.pkgs.buildPythonApplication rec {
	pname = "mivv";
	version = "0.1.0";

	src = ./.;
	nativeBuildInputs = [ qt5.wrapQtAppsHook python3.pkgs.setuptools ];

	propagatedBuildInputs = with python3.pkgs; [ pyqt5 qt5.qtsvg ];

	dontWrapQtApps = true;
	preFixup = ''
		wrapQtApp $out/bin/mivv
	'';
}
