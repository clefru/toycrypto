{ pkgs ? (import <nixpkgs> { })}:
with pkgs;
let mypython = (python3.withPackages (ps: [
      ps.yapf
      ps.mypy
    ]));
in pkgs.mkShell {
  buildInputs = [ mypython ];
  # TODO: Fix this path. "" + ./. sadly stages the directory.
  PYTHONPATH = "/home/clemens/devel/toycrypto";
}
