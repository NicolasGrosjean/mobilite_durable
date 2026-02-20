# OpenTopoData

OpenTopoData est utilisé pour obtenir une approximation de l'altitude.

C'est notamment utiliser pour prendre en compte le dénivelé lors du calcul de distances.

## Installation

**ATTENTION** Le jeu de données fait 21.6Go donc il faut au moins 43Go pour l'installer (archive + extraction).

```bash
cd ..
git clone https://github.com/ajnisbet/opentopodata.git
cd opentopodata
wget https://files.gpxz.io/eudem_buffered.zip
unzip eudem_buffered.zip
mv eudem data/
cat > config.yaml << EOF
datasets:
- name: eudem25m
  path: data/eudem
  filename_epsg: 3035
  filename_tile_size: 1000000
EOF
make build
make run
```

## Usage

```bash
curl http://localhost:5000/v1/eudem25m?locations=45.18,5.74
```

## Aller plus loin

Pour aller plus loin avec OpenTopoDta, vous pouvez consulter la [documentation](https://www.opentopodata.org/).
