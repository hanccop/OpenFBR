# statsbomb-to-fbr

Conversor de **StatsBomb Open Data** (datos de eventos) al formato **FBR 1.0**.

Es el primer conversor de entrada de FBR: demuestra que el formato carga **datos reales**,
no solo ejemplos hechos a mano. Con esto, un tercero puede tomar un partido público y
producir un `.fbr.json` conforme.

## Cómo funciona

StatsBomb Open Data trae, por cada evento (pase, tiro, etc.), una posición `[x,y]` sobre una
cancha de 120×80. FBR usa keyframes dispersos + interpolación, así que:

- se construyen **11 slots por equipo** (H01..H11 / A01..A11) con el modelo de identidad de FBR
  (persona / slot / ocupación): las **sustituciones cambian al ocupante del slot**, así que en
  cancha siempre hay 11 por lado y el dorsal del token cambia con el cambio;
- la trayectoria del **balón** sale de la posición de cada evento;
- la trayectoria de cada **slot** une las posiciones del titular hasta el cambio y las del
  suplente después;
- **goles**, **tarjetas** y **sustituciones** se mapean a eventos FBR (`subs` {in, out, slot});
  el marcador se recomputa de los goles.

Las posiciones son **on-ball** (StatsBomb de eventos no trae tracking continuo de los 22).
Es exactamente el caso de uso disperso de FBR, y queda dicho con honestidad.

## Uso

```bash
# 1) baja un partido de StatsBomb Open Data (github.com/statsbomb/open-data), p. ej. el 3869685:
curl -O https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/3869685.json
curl -O https://raw.githubusercontent.com/statsbomb/open-data/master/data/lineups/3869685.json

# 2) conviértelo a FBR:
python3 statsbomb_to_fbr.py 3869685_events.json 3869685_lineups.json \
    --home "Argentina" --away "France" --date 2022-12-18 \
    --match-id 3869685 --competition "FIFA World Cup 2022" \
    --out final2022.fbr.json

# 3) valida el resultado con el validador de referencia:
npx fbr-validate final2022.fbr.json      # → ✓ válido
```

`--home`/`--away` deben ser los nombres de equipo tal como aparecen en StatsBomb.
`--max-period 4` (por defecto) incluye hasta la prórroga y **excluye la tanda de penales**.

## Limitaciones (v1, honestas)

- Posiciones **on-ball**: entre toques, las trayectorias se interpolan; no es tracking real de los 22.
- El mapeo local/visitante se toma de `--home`/`--away`; verifícalo contra `matches.json`.

## Atribución y licencia (importante)

El **código** de este conversor es MIT (como el resto del código de OpenFBR).

Los **datos** de StatsBomb están bajo la **StatsBomb Open Data License** (uso no comercial, con
atribución). Por eso **este repositorio no incluye ningún `.fbr.json` derivado de StatsBomb**: se
generan localmente. Si publicas un FBR derivado, incluye la atribución:

> «Data provided by StatsBomb Open Data.»

y respeta su licencia. No mezcles datos no comerciales de StatsBomb con un uso comercial sin la
licencia correspondiente.
