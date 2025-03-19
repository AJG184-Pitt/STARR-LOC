# shell.nix
let
  pkgs = import <nixpkgs> {};

  python = pkgs.python3.override {
    self = python;
    packageOverrides = pyfinal: pyprev: {
      # pymap3d = pyfinal.callPackage ./pymap3d.nix { };
    };
  };

in pkgs.mkShell {
  packages = [
    (python.withPackages (python-pkgs: [
      # select Python packages here
      python-pkgs.pandas
      python-pkgs.pyqt6
      python-pkgs.sgp4
      python-pkgs.pyserial
    ]))
  ];
}
