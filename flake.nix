{
  description = "DRG Save Editor environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
  };

  outputs =
    { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          default = pkgs.mkShell {
            buildInputs = with pkgs; [
              python3
              zstd
              libGL
              fontconfig
              freetype
              libxkbcommon
              wayland
              libdecor
            ];

            shellHook = ''
              export LD_LIBRARY_PATH="${
                pkgs.lib.makeLibraryPath [
                  pkgs.zstd
                  pkgs.libGL
                  pkgs.fontconfig
                  pkgs.freetype
                  pkgs.libxkbcommon
                  pkgs.wayland
                  pkgs.libdecor
                ]
              }:$LD_LIBRARY_PATH"

              # Clear QT_PLUGIN_PATH so it only uses PySide6's bundled plugins
              unset QT_PLUGIN_PATH
              export QT_QPA_PLATFORM=wayland

              if [ -d "venv" ]; then
                source venv/bin/activate
              fi
            '';
          };
        }
      );
    };
}
