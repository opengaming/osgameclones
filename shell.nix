with import <nixpkgs> {};

stdenv.mkDerivation {
  name = "osgameclones";
  buildInputs = [
    python27
    python27Packages.virtualenv
  ];
  shellHook = ''
    export LC_ALL=en_US.UTF-8
    export LANG=en_US.UTF-8
    virtualenv --no-setuptools .venv
    export PATH=$PWD/.venv/bin:$PATH
    export PIPENV_VENV_IN_PROJECT=1
    pip install --upgrade pip
    pip install --upgrade pipenv
    pipenv sync --dev
  '';
}
