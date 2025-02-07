
```
sudo apt update; sudo apt install -y python3 virtualenv direnv curl
curl -fsSL https://deb.nodesource.com/setup_23.x | sudo -E bash -
sudo apt update; sudo apt install -y nodejs
virtualenv -p /usr/bin/python3 venv
#venv/bin/pip install -r requirements.txt
#venv/bin/pre-commit install
sed -nr '/direnv hook bash/!p;$aeval "\$(direnv hook bash)"' -i ~/.bashrc
source ~/.bashrc
cd frontend; npm install; cd ..
ln -s ng.js frontend/node_modules/@angular/cli/bin/ng
echo -e "source venv/bin/activate\nunset PS1\nPATH_add frontend/node_modules/@angular/cli/bin\nsource <(ng completion script)" > .envrc
direnv allow
```
