# Informe de conformidad FBR

_Generado: 2026-07-02 01:07_

**Resultado final: APROBADO**

Válidos: 3 · Inválidos: 21

```

[1] ARCHIVOS VÁLIDOS (deben aprobar)
  ✓ completo.fbr.json: aceptado
  ✓ minimo.fbr.json: aceptado
  ✓ multi-balon.fbr.json: aceptado

[2] ARCHIVOS INVÁLIDOS (deben rechazarse, con motivo)
  ✓ 01_falta_requerido_pitch.fbr.json: rechazado — schema: 'pitch' is a required property
  ✓ 02_tipo_incorrecto_version.fbr.json: rechazado — schema: 1.0 is not of type 'string'
  ✓ 03_fuera_de_rango_confidence.fbr.json: rechazado — schema: 1.5 is greater than the maximum of 1
  ✓ 04_propiedad_adicional_raiz.fbr.json: rechazado — schema: Additional properties are not allowed ('foo_desconocido' was unexpected)
  ✓ 05_role_fuera_de_enum.fbr.json: rechazado — schema: 'Midfielder' is not one of ['GK', 'SW', 'CB', 'LB', 'RB', 'LWB', 'RWB', 'CDM', 'CM', 'CAM', 'LM', 'RM', 'LW', 'RW', 'CF', 'ST', 'referee', 'assistant', 'fourth', 'var']
  ✓ 06_ballstate_invalido.fbr.json: rechazado — schema: [20, 0.4, 0.44, 'fuera'] is too long
  ✓ 07_anchor_ausente_jugador_campo.fbr.json: rechazado — schema: 'anchor' is a required property
  ✓ 08_sustitucion_sin_subs.fbr.json: rechazado — schema: 'subs' is a required property
  ✓ 09_id_duplicado.fbr.json: rechazado — semántica: IDs duplicados: CI2
  ✓ 10_referencia_inexistente.fbr.json: rechazado — semántica: referencia inexistente en evento (actor=ZZ99)
  ✓ 11_tiempo_negativo.fbr.json: rechazado — semántica: evento fuera del partido: t=-5 (shot)
  ✓ 12_evento_fuera_del_partido.fbr.json: rechazado — semántica: evento fuera del partido: t=99999 (shot)
  ✓ 13_fecha_no_iso.fbr.json: rechazado — schema: '30/06/2026' is not a 'date'
  ✓ 14_marcador_inconsistente.fbr.json: rechazado — semántica: marcador inconsistente: goles contados {'home': 1, 'away': 2} vs meta.score {'home': 3, 'away': 2}
  ✓ 15_json_invalido.fbr.json: rechazado (carga) — JSON inválido: Expecting property name enclosed in double quotes: line 1 column 36 (char 35)
  ✓ 16_archivo_vacio.fbr.json: rechazado (carga) — archivo vacío
  ✓ 17_coordenada_fuera_de_rango.fbr.json: rechazado — semántica: coordenada imposible en BALL: (9.0,0.44)
  ✓ 18_sub_persona_inexistente.fbr.json: rechazado — semántica: cambio referencia persona inexistente (in=xx-nadie)
  ✓ 19_occupants_con_hueco.fbr.json: rechazado — semántica: occupants de CI1 con hueco/solape entre tramos
  ✓ 20_lineup_incompleto.fbr.json: rechazado — semántica: lineup de home no tiene 11 titulares (tiene 10)
  ✓ 21_goal_subtype_invalido.fbr.json: rechazado — schema: 'golazo' is not one of ['normal', 'penalty', 'own_goal', 'free_kick', 'header']

[3] MÓDULOS FUNCIONALES (archivo completo)
  módulos: meta, pitch, teams, actors, time, tracks, events, analytics, render, extensions
  lineup en teams: sí

[6] TIMELINE
  periodos: 2 · pausas (hidratación): 2

[8] INTERNACIONALIZACIÓN (i18n)
  de: 66 claves, alineado
  en: 66 claves, alineado
  es: 66 claves, alineado
  fr: 66 claves, alineado
  it: 66 claves, alineado
  pt: 66 claves, alineado

============================================================
  [OK] Todos los válidos aceptados
  [OK] Todos los inválidos rechazados
  [OK] Módulos funcionales presentes
  [OK] Timeline con periodos y pausas
  [OK] i18n alineado (en/es/fr/pt)
============================================================
 RESULTADO FINAL: APROBADO
============================================================
```
