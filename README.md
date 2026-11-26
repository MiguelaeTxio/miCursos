# miCursos

Repositorio público de **temarios de cursos de idiomas** para la app
Android [miA2F](https://github.com/MiguelaeTxio/miA2F). Solo contiene
contenido: ni código de la app ni datos personales de nadie.

Cada curso vive en su propia carpeta (`{idioma}/{nivel}/`). El
primero es **francés A2** (`fr/A2/`). La app descarga el curso, lo
guarda en el móvil y comprueba su versión; corregir o ampliar un
temario aquí no exige sacar una versión nueva de la app.

---

## Fuentes del temario de francés A2

El temario se ciñe al **Marco Común Europeo de Referencia para las
Lenguas (MCER)**, nivel A2. No se redacta de memoria: cada unidad del
curso indica de qué fuente sale lo que enseña.

| # | Fuente | Para qué se usa |
|---|---|---|
| 1 | Consejo de Europa, *Common European Framework of Reference for Languages: Learning, teaching, assessment — Companion volume*, Estrasburgo, 2020 (versión francesa: *Cadre européen commun de référence pour les langues — Volume complémentaire*). PDF: <https://rm.coe.int/16809ea0d4> | Objetivos «soy capaz de…» (`canDo`) de cada unidad: descriptores del nivel A2 por actividad comunicativa (comprensión, expresión e interacción oral y escrita, mediación). |
| 2 | Consejo de Europa, buscador oficial de descriptores del MCER: <https://www.coe.int/web/common-european-framework-reference-languages/cefr-descriptors-search> | Comprobar la redacción exacta y el nivel de cada descriptor citado. |
| 3 | Jean-Claude Beacco (dir.), Sylvie Lepage, Rémy Porquier y Patrick Riba, *Niveau A2 pour le français (utilisateur/apprenant élémentaire) niveau intermédiaire : un référentiel*, Conseil de l'Europe / Didier, París, 2008. Es la descripción oficial del nivel A2 para el francés dentro de las *Descriptions de niveaux de référence* (DNR) del Consejo de Europa. Capítulo 5 (inventario gramatical) consultado en <https://bop.fipf.org/wp-content/uploads/2017/03/refa343342.pdf> | Qué gramática, conectores y formas lingüísticas entran en el A2 de francés (tiempos verbales, pronombres, determinantes, negación, interrogación, marcadores de tiempo, conectores). Fija también lo que **no** se exige todavía en A2 (por ejemplo, el imparfait y el futuro solo para algunos verbos). |

| 4 | Jean-Thierry Le Bougnec y Marie-José Lopes, *Inspire 2* (A2), Hachette FLE, París, 2020: *Précis de phonétique* del libro del alumno. PDF: <https://inspire.hachettefle.fr/ressources/INSP2_LE_PDF/INSP2_precisphonetique.pdf> (`inspire2-2020`) | Puntos de pronunciación del A2 de francés (ritmo, liaison, encadenamiento, vocales y consonantes), porque el capítulo «Matière sonore» del referencial A2 (fuente 3) no está accesible en línea. El MCER (fuente 1) solo describe la inteligibilidad y la prosodia del A2, no una lista de sonidos. |

Si una unidad necesita una fuente distinta, se añade a esta tabla
antes de usarla.

---

## Formato de los archivos (versión 1)

### `index.json` (raíz)

Lista de cursos disponibles. La app lo lee primero.

```json
{
  "schemaVersion": 1,
  "courses": [
    {
      "id": "fr-a2",
      "language": "fr",
      "level": "A2",
      "title": "Francés A2 (MCER)",
      "path": "fr/A2/course.json",
      "version": 1
    }
  ]
}
```

- `version` es la versión del temario de ese curso. Se sube en uno
  cada vez que cambia su `course.json`; la app la compara con la que
  tiene guardada para saber si debe descargarlo de nuevo.

### `course.json` (uno por curso)

```json
{
  "schemaVersion": 1,
  "id": "fr-a2",
  "language": "fr",
  "instructionLanguage": "es",
  "level": "A2",
  "version": 1,
  "title": "Francés A2 (MCER)",
  "sources": [
    { "id": "beacco-a2-2008", "title": "Niveau A2 pour le français…", "url": "…" }
  ],
  "units": [
    {
      "id": "fr-a2.u01",
      "number": 1,
      "title": "…",
      "canDo": [
        { "text": "Puedo…", "sourceId": "cefr-cv-2020" }
      ],
      "concepts": [
        {
          "id": "fr-a2.u01.passe-compose-etre",
          "type": "grammar",
          "title": "Passé composé con être",
          "explanation": "Explicación breve en castellano.",
          "examples": ["Nous sommes allés au cinéma."],
          "sourceIds": ["beacco-a2-2008"]
        }
      ]
    }
  ]
}
```

| Campo | Regla |
|---|---|
| `instructionLanguage` | Idioma de las explicaciones (`es`). |
| `sources[]` | Fuentes del curso; cada `id` es único. `url` es opcional. |
| `units[].id` | Empieza por el `id` del curso más un punto. Único. |
| `units[].number` | Correlativo desde 1, en orden de estudio. |
| `units[].canDo[]` | Objetivos «soy capaz de…» en castellano, cada uno con la fuente (`sourceId`) de la que sale. |
| `concepts[].id` | Empieza por el `id` de su unidad más un punto. Único en todo el curso. |
| `concepts[].type` | `grammar`, `vocabulary`, `communication` o `phonetics`. |
| `concepts[].explanation` | En castellano, breve; la desarrolla la profesora en las sesiones. |
| `concepts[].examples[]` | Frases en el idioma del curso, al menos una. |
| `concepts[].sourceIds[]` | Fuentes del concepto; deben existir en `sources`. |

**Los identificadores son permanentes.** El progreso de los alumnos
apunta a ellos, así que una vez publicado un `id` no se renombra ni se
reutiliza para otra cosa: si un concepto cambia de sentido, se crea
uno nuevo.

### Validación

Antes de cada commit que toque un curso:

```bash
python3 tools/validate_course.py
```

Comprueba el formato de `index.json` y de cada `course.json`, que los
identificadores sean únicos y tengan el prefijo correcto, que las
unidades estén numeradas desde 1 y que toda fuente citada exista. Deja
además su salida en `validate_course.log`, que no se versiona.
