{pkgs}: {
  deps = [
    pkgs.htop
    pkgs.python311Packages.uvicorn
  ];
}
