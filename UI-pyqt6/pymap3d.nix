# toolz.nix
{
  lib,
  buildPythonPackage,
  fetchPypi,
  setuptools,
  wheel,
}:

buildPythonPackage rec {
  pname = "pymap3d";
  version = "3.1.0";

  src = fetchPypi {
    inherit pname version;
    hash = "sha256-wag/wnMiNLZ2PwNyrSYo3SSxOh5qZOn3glvkESRj82k=";
  };

  # do not run tests
  doCheck = false;

  # specific to buildPythonPackage, see its reference
  pyproject = true;
  build-system = [
    setuptools
    wheel
  ];
}
