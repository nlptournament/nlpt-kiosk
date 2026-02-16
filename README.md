# NLPT-Kiosk(-Controller)

Ziel: System um aus einer Oberfläche heraus alle Kiosk-Clients (Beamer) zu steuern und synchronisieren.

Soll bieten: Loops von Statistiken, Ankündigungen während des normalen Events. Aber auch AdHoc-Anzeige von Informationen, Videos oder statischen Bildern während Präsentationen oder der Nachtpause.

## Infos für Dimi

Die Anzeigen, welche von den Beamern präsentiert werden, sollen ordentlich aussehen und der "Marke" NLPT entsprechen. Ich habe so einige Unzulänglichkeiten was das Thema Design angeht, daher würde ich das Tehma lieber in deine Hände übergeben.

Bitte nur auf dem **styling** Branch arbeiten, diesen werde ich in Ruhe lassen, bis du ferig bist. Und ich werde auf meinem dev Branch (wo ich mich schonmal um das Backend kümmere) dafür sorgen, dass dein styling Branch mergebar bleibt.

Ich arbeite wieder mit Angular habe dir dieses mal aber auch Tailwind eingebunden, das habe ich als größte Kritik mitgenommen ;)  
Wenn du ein Dev-Setup wi (oder ähnlich) dem weiter unten beschriebenen hast. Musst du eigentlich nur ins frontend Verzeichnis wechseln und `ng serve` ausführen und solltest alles haben was du fürs styling brauchst. Auf allen Seiten sind Beispieldaten enthalten, wenn du minimum diese alle auf einem Sceen unter bekommst passt das für mich, wenn du mehr unterbringst ist gut, aber achte darauf, dass Schriften und Ähnliches nich tzu klein werden. Es muss ja aus ein paar Metern Entfernung erkennbar sein.

Der Dev-Server ist zu erreichen unter: [http://localhost:4200](http://localhost:4200)  
Du wirst von einer Index-Seite begrüßt (auf dieser musst du nichts anpassen, ist nur für Dev-Zwecke) die dich auf alle Seiten bringt, die ich dich bitte hübsch zu machen.

Ein paar Worte zu Tailwind: Ich habe, wie du sehen wirst, in der `tailwind.config.js` alle Werte, die Abstände oder Größen definieren, auf eine **vw** Basis umgeschrieben. Dies soll dafür sorgen, dass ein Screen immer gleich aussieht solange er eine 16:9 Auflösung hat. Die Auflösung der Beamer ist derzeit noch nicht bekannt und sie können unter Umständen auch unterschiedliche Auflösungen haben. Achso: Und um die nervigen Scrollbars zu verhindern, habe ich auf allen Screens soweit, den vertikalen Overflow verboten, das auch bitte beibehalten.  
Du musst also darauf achten, dass dein Browser eine 16:9 Auflösung darstellt, wenn du die Elemente ausrichtest, damit zum schluss alles passt. Solltest du außerdem weitere Abstände oder Größen benötigen, so bitte ich dich auch diese in der config mit einem vw Wert zu definieren.

> [!NOTE]
> Bei einer Browser-Breite von 2560px entsprechen alle Größen wieder ihren ursprünglichen rem Werten.

Alles was ich bisher an "Design" gemacht habe, ist nur eine Idee. So könnte ich mir die Screens grb vorstellen. Feel free alles weg zu werfen und neu zu machen, falls du es für angebracht hältst ;) ... Es soll zum Schluss hübsch sein und nach NLPT aussehen ^^

Und wenn du zu irgendwas Fragen hast, oder etwas unklar ist, immer gerne bei mir melden, soll ja, wie immer, perfekt werden ;)

Und nun, der Vollständigkeithalber, alle Dateien, um die ich dich bitte, zu kümmern:

  * `frontend/src/app/components/announcements/announcements.component.html`
  * `frontend/src/app/components/player-counts/player-counts.component.html`
  * `frontend/src/app/components/tas/tas.component.html`
  * `frontend/src/app/components/timer/timer.component.html`

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
