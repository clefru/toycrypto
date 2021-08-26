{ pkgs ? (import <nixpkgs> { })}:
with pkgs;
let mypython = (python2.withPackages (ps: [
      ps.yapf
    ]));
in pkgs.mkShell {
  buildInputs = [ mypython ];
}


