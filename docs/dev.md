## Dev Info

## Development Environment Setup

Folgende Schritte nutze ich für mein Dev-Setup auf Ubuntu, funktioniert genauso in einer Ubuntu WSL2 unter Windows.  
Muss aber unter Umständen für andere Umgebungen adaptiert werden.

```
sudo apt update; sudo apt install -y python3 virtualenv direnv curl
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt update; sudo apt install -y nodejs
virtualenv -p /usr/bin/python3 venv
venv/bin/pip install -r requirements.txt
venv/bin/pre-commit install
sed -nr '/direnv hook bash/!p;$aeval "\$(direnv hook bash)"' -i ~/.bashrc
source ~/.bashrc
cd frontend; npm install; cd ..
ln -s ng.js frontend/node_modules/@angular/cli/bin/ng
echo -e "source venv/bin/activate\nunset PS1\nPATH_add frontend/node_modules/@angular/cli/bin\nsource <(ng completion script)" > .envrc
direnv allow
```

## Setup Build-Environment

```
sudo docker buildx create --name multi-arch --platform "linux/arm64,linux/amd64,linux/arm/v7" --driver "docker-container"
sudo docker buildx use multi-arch
sudo docker buildx inspect --bootstrap
```

## Styling of Screens

Ein paar Worte zu Tailwind: Ich habe, wie du sehen wirst, in der `tailwind.config.js` alle Werte, die Abstände oder Größen definieren, auf eine **vw** Basis umgeschrieben. Dies soll dafür sorgen, dass ein Screen immer gleich aussieht solange er eine 16:9 Auflösung hat. Die Auflösung der Beamer ist derzeit noch nicht bekannt und sie können unter Umständen auch unterschiedliche Auflösungen haben. Achso: Und um die nervigen Scrollbars zu verhindern, habe ich auf allen Screens soweit, den vertikalen Overflow verboten, das auch bitte beibehalten.  
Du musst also darauf achten, dass dein Browser eine 16:9 Auflösung darstellt, wenn du die Elemente ausrichtest, damit zum schluss alles passt. Solltest du außerdem weitere Abstände oder Größen benötigen, so bitte ich dich auch diese in der config mit einem vw Wert zu definieren.

> [!NOTE]
> Bei einer Browser-Breite von 2560px entsprechen alle Größen wieder ihren ursprünglichen rem Werten.
