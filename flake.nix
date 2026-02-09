{
  description = "DRG Save Editor flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      packages = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          pythonEnv = pkgs.python3.withPackages (
            ps: with ps; [
              pyqt6
              pyside6
            ]
          );
        in
        {
          default = pkgs.stdenv.mkDerivation {
            pname = "drg-save-editor";
            version = "git";
            src = ./.;

            nativeBuildInputs = [ pkgs.makeWrapper ];

            installPhase = ''
              mkdir -p $out/share/drg-save-editor
              cp -r src $out/share/drg-save-editor/
              cp guids.json $out/share/drg-save-editor/
              cp editor.ui $out/share/drg-save-editor/
              cp readme.md $out/share/drg-save-editor/

              mkdir -p $out/bin
              makeWrapper ${pythonEnv}/bin/python $out/bin/drg-save-editor \
                --add-flags "$out/share/drg-save-editor/src/main/python/main.py" \
                --set QT_QPA_PLATFORM "" \
                --chdir "$out/share/drg-save-editor"
            '';
          };
        }
      );

      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          pythonEnv = pkgs.python3.withPackages (
            ps: with ps; [
              pyqt6
              pyside6
            ]
          );
        in
        {
          default = pkgs.mkShell {
            buildInputs = [ pythonEnv ];

            shellHook = ''
              # Support both Wayland and X11
              export QT_QPA_PLATFORM="''${QT_QPA_PLATFORM:-}"
            '';
          };
        }
      );
    };
}
