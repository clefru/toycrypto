{ pkgs ? (import <nixpkgs> { })}:
with pkgs;
let mypython = (python3.withPackages (ps: [
      ps.yapf
      ps.mypy
    ]));
in pkgs.mkShell {
  buildInputs = [ mypython ];
  PYTHONPATH = builtins.toPath ./.;
}
