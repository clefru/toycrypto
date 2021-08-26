{ pkgs ? (import <nixpkgs> { })}:
with pkgs;
let mypython = (python3.withPackages (ps: [
      ps.yapf
    ]));
in pkgs.mkShell {
  buildInputs = [ mypython ];
}


