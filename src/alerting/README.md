# Quick start

Cloner le projet gitlab

```bash
git clone git@gitlab.polytech.umontpellier.fr:pwa-group-b/doremix.git
```

Aller dans le dossier src/alerting.

```bash
cd src/alerting
```

Lancer l'infrastructure.

```bash
docker composer up
```

## Ajouter une sonde

Modifier le fichier ```monitors.json``` et ajouter un object littéral.

Détruire l'infrastructure
```bash
docker composer down
```

Reconstruire l'infrastructure
```bash
docker composer up
```
