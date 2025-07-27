{ pkgs, ... }: {

packages = with pkgs; [

python311

git

];

# Optional Firebase Studio integration (safe and valid):
 idx.extensions = [ "ms-python.python"  "ms-python.debugpy"];
}