## Dev Info

## Development Environment Setup

The following steps outline the development setup on Ubuntu and also work in an Ubuntu WSL2 environment on Windows. Adjustments may be needed for other distributions or environments.

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

The `tailwind.config.js` uses **vw** units for all spacing and size values. This ensures screens maintain consistent proportions on 16:9 displays, since projector resolutions may vary. Vertical overflow is disabled across all screens to prevent scrollbars — please keep this behavior when making changes.  
When aligning elements, ensure your browser viewport has a 16:9 aspect ratio so everything renders correctly. If you need additional spacing or size values, define them using vw units in the config.

> [!NOTE]
> At a browser width of 2560px, all vw values correspond to their original rem equivalents.

## Chromium Infos

For Kiosks it's recomended to disable some "security" features in Chromium for a smooth experience.

disable CORS: `--user-data-dir="/tmp/chrome-dev-data" --disable-web-security`

allow auto-play for videos: `--autoplay-policy=no-user-gesture-required`

Chromium startcommand for testing:

```
chromium-browser http://localhost:4200/?name=testkiosk1 --no-first-run --autoplay-policy=no-user-gesture-required --user-data-dir="/tmp/chrome-dev-data" --disable-web-security
```

## Testing Stream

A Stream for testing can be found here: `https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8` (it's the Big Buck Bunny)
