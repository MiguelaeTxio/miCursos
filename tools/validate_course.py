"""
Validates miCursos files: the root index.json and every course.json
it lists, against the v1 format documented in README.md.
---
Valida los archivos de miCursos: el index.json raíz y cada course.json
que enumera, contra el formato v1 documentado en README.md.

Uso / Usage:
    python3 tools/validate_course.py [ruta_raiz_del_repositorio]
"""

import json
import os
import sys
from datetime import datetime

SCHEMA_VERSION = 1
CONCEPT_TYPES = ("grammar", "vocabulary", "communication", "phonetics")
LOG_FILE_NAME = "validate_course.log"

_log_file = None


def _log(message):
    """
    Prints a timestamped line and appends it to the log file, flushing
    both at once.
    ---
    Imprime una línea con hora y la añade al archivo de log, vaciando
    los dos búferes a la vez.
    """
    line = "[%s] %s" % (datetime.now().strftime("%H:%M:%S"), message)
    print(line, flush=True)
    if _log_file is not None:
        _log_file.write(line + "\n")
        _log_file.flush()


def _log_plain(message):
    """
    Same as _log but without timestamp, for the final summary.
    ---
    Igual que _log pero sin hora, para el resumen final.
    """
    print(message, flush=True)
    if _log_file is not None:
        _log_file.write(message + "\n")
        _log_file.flush()


class Report:
    """
    Collects validation errors for one file.
    ---
    Reúne los errores de validación de un archivo.
    """

    def __init__(self, path):
        self.path = path
        self.errors = []

    def error(self, where, message):
        """
        Records and logs an error.
        ---
        Registra y escribe en el log un error.
        """
        text = "%s: %s" % (where, message)
        self.errors.append(text)
        _log("  ERROR %s" % text)


def _require(report, obj, key, kind, where):
    """
    Checks that obj[key] exists and has the expected type.
    ---
    Comprueba que obj[key] existe y tiene el tipo esperado.
    """
    if not isinstance(obj, dict) or key not in obj:
        report.error(where, "falta el campo '%s'" % key)
        return None
    value = obj[key]
    if not isinstance(value, kind) or isinstance(value, bool) and \
            kind is not bool:
        report.error(where, "'%s' no es del tipo esperado" % key)
        return None
    if isinstance(value, (str, list)) and len(value) == 0:
        report.error(where, "'%s' está vacío" % key)
        return None
    return value


def _check_text_list(report, items, where):
    """
    Checks a non-empty list of non-empty strings.
    ---
    Comprueba una lista no vacía de cadenas no vacías.
    """
    for index, item in enumerate(items, start=1):
        if not isinstance(item, str) or not item.strip():
            report.error("%s[%d]" % (where, index),
                         "texto vacío o no válido")


def validate_course(path, expected):
    """
    Validates one course.json against the index entry that points to
    it. Returns the Report.
    ---
    Valida un course.json contra la entrada del índice que apunta a
    él. Devuelve el Report.
    """
    report = Report(path)
    _log("Validando %s" % path)
    try:
        with open(path, encoding="utf-8") as handle:
            course = json.load(handle)
    except (OSError, ValueError) as exc:
        report.error(path, "no se puede leer como JSON (%s)" % exc)
        return report

    if course.get("schemaVersion") != SCHEMA_VERSION:
        report.error("curso", "schemaVersion debe ser %d" % SCHEMA_VERSION)
    for key in ("id", "language", "level"):
        value = _require(report, course, key, str, "curso")
        if value is not None and value != expected.get(key):
            report.error("curso", "'%s' no coincide con index.json" % key)
    version = _require(report, course, "version", int, "curso")
    if version is not None and version != expected.get("version"):
        report.error("curso", "'version' no coincide con index.json")
    _require(report, course, "title", str, "curso")
    _require(report, course, "instructionLanguage", str, "curso")

    course_id = course.get("id", "")
    source_ids = set()
    for index, source in enumerate(
            _require(report, course, "sources", list, "curso") or [],
            start=1):
        where = "sources[%d]" % index
        source_id = _require(report, source, "id", str, where)
        _require(report, source, "title", str, where)
        if source_id in source_ids:
            report.error(where, "id de fuente repetido '%s'" % source_id)
        if source_id:
            source_ids.add(source_id)

    seen_ids = set()
    units = _require(report, course, "units", list, "curso") or []
    for unit_index, unit in enumerate(units, start=1):
        where = "units[%d]" % unit_index
        unit_id = _require(report, unit, "id", str, where)
        number = _require(report, unit, "number", int, where)
        if number is not None and number != unit_index:
            report.error(where, "number debe ser %d" % unit_index)
        _require(report, unit, "title", str, where)
        if unit_id:
            if not unit_id.startswith(course_id + "."):
                report.error(where, "el id debe empezar por '%s.'"
                             % course_id)
            if unit_id in seen_ids:
                report.error(where, "id repetido '%s'" % unit_id)
            seen_ids.add(unit_id)

        for can_index, can_do in enumerate(
                _require(report, unit, "canDo", list, where) or [],
                start=1):
            can_where = "%s.canDo[%d]" % (where, can_index)
            _require(report, can_do, "text", str, can_where)
            source = _require(report, can_do, "sourceId", str, can_where)
            if source and source not in source_ids:
                report.error(can_where, "sourceId desconocido '%s'" % source)

        concepts = _require(report, unit, "concepts", list, where) or []
        for concept_index, concept in enumerate(concepts, start=1):
            c_where = "%s.concepts[%d]" % (where, concept_index)
            concept_id = _require(report, concept, "id", str, c_where)
            if concept_id:
                if unit_id and not concept_id.startswith(unit_id + "."):
                    report.error(c_where, "el id debe empezar por '%s.'"
                                 % unit_id)
                if concept_id in seen_ids:
                    report.error(c_where, "id repetido '%s'" % concept_id)
                seen_ids.add(concept_id)
            kind = _require(report, concept, "type", str, c_where)
            if kind and kind not in CONCEPT_TYPES:
                report.error(c_where, "type no válido '%s'" % kind)
            _require(report, concept, "title", str, c_where)
            _require(report, concept, "explanation", str, c_where)
            examples = _require(report, concept, "examples", list, c_where)
            if examples:
                _check_text_list(report, examples, c_where + ".examples")
            for source in _require(report, concept, "sourceIds", list,
                                   c_where) or []:
                if source not in source_ids:
                    report.error(c_where,
                                 "sourceId desconocido '%s'" % source)
        _log("  Unidad %d: %d conceptos revisados"
             % (unit_index, len(concepts)))
    return report


def main(root):
    """
    Validates index.json and every course it lists. Exit code 0 only
    if there are no errors.
    ---
    Valida index.json y cada curso que enumera. Código de salida 0
    solo si no hay errores.
    """
    global _log_file
    _log_file = open(os.path.join(root, LOG_FILE_NAME), "a",
                     encoding="utf-8")
    _log("Inicio de la validación en %s" % os.path.abspath(root))
    reports = []
    index_report = Report("index.json")
    reports.append(index_report)
    try:
        with open(os.path.join(root, "index.json"), encoding="utf-8") as h:
            index = json.load(h)
    except (OSError, ValueError) as exc:
        index_report.error("index.json", "no se puede leer (%s)" % exc)
        index = {}

    if index and index.get("schemaVersion") != SCHEMA_VERSION:
        index_report.error("index.json",
                           "schemaVersion debe ser %d" % SCHEMA_VERSION)
    entries = _require(index_report, index, "courses", list,
                       "index.json") or []
    for entry_index, entry in enumerate(entries, start=1):
        where = "courses[%d]" % entry_index
        for key in ("id", "language", "level", "title", "path"):
            _require(index_report, entry, key, str, where)
        _require(index_report, entry, "version", int, where)
        if isinstance(entry, dict) and isinstance(entry.get("path"), str):
            reports.append(validate_course(
                os.path.join(root, entry["path"]), entry))

    total = sum(len(report.errors) for report in reports)
    _log_plain("")
    _log_plain("RESUMEN")
    for report in reports:
        _log_plain("  %s: %d errores" % (report.path, len(report.errors)))
    _log_plain("  Total: %d errores" % total)
    _log_file.close()
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
