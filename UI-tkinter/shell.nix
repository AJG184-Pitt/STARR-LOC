{ pkgs ? import <nixpkgs> {} }:

let
  # Create a custom Python environment
  python-with-my-packages = pkgs.python311.withPackages (ps: with ps; [
    numpy
    toolz
    sgp4
    tkinter
    pytz
    # pymap3d is missing
  ]);
in
pkgs.mkShell {
  buildInputs = [
    python-with-my-packages
    # Add pip so we can install pymap3d
    pkgs.python311Packages.pip
  ];

  # This shell hook will run when you enter the shell
  shellHook = ''
    # Create a virtual environment if it doesn't exist
    if [ ! -d .venv ]; then
      python -m venv .venv
    fi
    # Activate the virtual environment
    source .venv/bin/activate
    # Install pymap3d if not already installed
    pip list | grep -q pymap3d || pip install pymap3d

    echo "Python environment ready with pymap3d installed in the virtual environment"
  '';
}
