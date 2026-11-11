from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zipfile import ZipFile
from xml.etree import ElementTree as ET


ROOT_DIR = Path(__file__).resolve().parent
DOCS_DIR = ROOT_DIR / "docs"
BASE_FILE = DOCS_DIR / "Desafio1_Dataset_Participantes.xlsx"
DEMO_FILE = DOCS_DIR / "Desafio1_Respostas_Novas_DEMO_JURI.xlsx"
REFERENCE_DATE = datetime(2026, 11, 12)

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def _column_number(reference: str) -> int:
    result = 0
    for character in reference:
        if not character.isalpha():
            break
        result = result * 26 + ord(character.upper()) - 64
    return result - 1


def read_xlsx(path: Path, sheet_name: str) -> list[list[str]]:
    with ZipFile(path) as archive:
        strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            strings = [
                "".join(text.text or "" for text in item.findall(".//m:t", NS))
                for item in root.findall("m:si", NS)
            ]

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(
            archive.read("xl/_rels/workbook.xml.rels")
        )
        relation_map = {
            item.attrib["Id"]: item.attrib["Target"].replace("\\", "/")
            for item in relationships
        }

        target = None
        for sheet in workbook.find("m:sheets", NS):
            if sheet.attrib["name"] == sheet_name:
                target = relation_map[sheet.attrib[REL_ID]].lstrip("/")
                break
        if target is None:
            raise ValueError(f"Sheet not found: {sheet_name}")
        while target.startswith("../"):
            target = target[3:]
        if not target.startswith("xl/"):
            target = f"xl/{target}"

        worksheet = ET.fromstring(archive.read(target))
        rows: list[dict[int, str]] = []
        for row in worksheet.findall(".//m:sheetData/m:row", NS):
            values: dict[int, str] = {}
            for cell in row.findall("m:c", NS):
                value = cell.findtext("m:v", default="", namespaces=NS)
                if cell.attrib.get("t") == "s" and value:
                    value = strings[int(value)]
                values[_column_number(cell.attrib.get("r", ""))] = value
            rows.append(values)

        width = max((max(row) for row in rows if row), default=-1) + 1
        return [[row.get(index, "") for index in range(width)] for row in rows]


def _records(path: Path, sheet_name: str) -> list[dict[str, str]]:
    rows = read_xlsx(path, sheet_name)
    if not rows:
        return []
    headers = rows[0]
    return [
        {headers[index]: value for index, value in enumerate(row) if headers[index]}
        for row in rows[1:]
    ]


def _parse_date(value: str) -> datetime | None:
    try:
        return datetime(1899, 12, 30) + timedelta(days=float(value))
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def load_managers() -> dict[str, str]:
    return {
        row.get("Gestor_Projeto", "").strip(): row.get("Email", "").strip()
        for row in _records(BASE_FILE, "Gestores_Projeto")
        if row.get("Gestor_Projeto", "").strip()
    }


def load_projects() -> list[dict[str, Any]]:
    actions = _records(BASE_FILE, "Acoes_GTraining")
    projects: dict[str, dict[str, Any]] = {}
    for action in actions:
        project_id = action.get("ID_Projeto", "").strip()
        if not project_id:
            continue
        project = projects.setdefault(
            project_id,
            {
                "id": project_id,
                "actions": [],
                "area": action.get("Area", ""),
                "client": action.get("Cliente", ""),
                "project_manager": action.get("Gestor_Projeto", "").strip(),
            },
        )
        project["actions"].append(action)

    managers = load_managers()
    result = []
    for project in projects.values():
        dates = [_parse_date(action.get("Data_Fim", "")) for action in project["actions"]]
        dates = [date for date in dates if date]
        states = [action.get("Estado", "").strip().lower() for action in project["actions"]]
        last_date = max(dates) if dates else None
        if all(state in {"concluída", "concluida"} for state in states) and last_date:
            status = "concluído" if last_date <= REFERENCE_DATE else "futuro"
        else:
            status = "incompleto"
        pending_actions = [
            action.get("ID_Projeto", "") + " / " + action.get("Estado", "").strip()
            for action in project["actions"]
            if action.get("Estado", "").strip().lower()
            not in {"concluída", "concluida"}
        ]
        if status == "incompleto":
            task = "Acompanhar ações pendentes"
            queue = "in_progress"
        elif status == "futuro":
            task = "Aguardar conclusão do projeto"
            queue = "waiting"
        else:
            task = "Confirmar ou preparar envio do questionário"
            queue = "action_required"
        result.append(
            {
                **project,
                "action_count": len(project["actions"]),
                "manager_email": managers.get(project["project_manager"]),
                "last_action_date": last_date.strftime("%Y-%m-%d") if last_date else None,
                "status": status,
                "queue": queue,
                "task": task,
                "pending_actions": pending_actions,
            }
        )
    return sorted(result, key=lambda project: project["id"])


def load_demo_updates() -> list[dict[str, Any]]:
    rows = read_xlsx(DEMO_FILE, "Respostas_Impulsa")
    updates = []
    for row in rows:
        if not any(row):
            continue
        response_id = row[0].strip() if row else ""
        if not response_id or not response_id.isdigit():
            continue
        nps = row[17].strip() if len(row) > 17 else ""
        updates.append(
            {
                "response_id": response_id,
                "nps": int(nps) if nps.isdigit() else None,
                "has_project": False,
                "has_responsible": False,
                "source": DEMO_FILE.name,
            }
        )
    return updates


def build_notifications(updates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    notifications = []
    for update in updates:
        reasons = []
        if update["nps"] is not None and update["nps"] <= 6:
            reasons.append(f"NPS baixo ({update['nps']})")
        if not update["has_project"]:
            reasons.append("resposta sem ID_Projeto")
        if not update["has_responsible"]:
            reasons.append("responsável não identificável")
        notifications.append(
            {
                "id": f"notification-{update['response_id']}",
                "response_id": update["response_id"],
                "type": "human_review" if not update["has_responsible"] else "satisfaction_alert",
                "status": "pending",
                "recipient": None,
                "reasons": reasons,
                "message": (
                    "Revisão humana necessária: não é seguro encaminhar esta "
                    "notificação sem projeto e responsável."
                ),
            }
        )
    return notifications


def build_snapshot() -> dict[str, Any]:
    projects = load_projects()
    dashboard_projects = [
        {key: value for key, value in project.items() if key != "actions"}
        for project in projects
    ]
    updates = load_demo_updates()
    notifications = build_notifications(updates)
    return {
        "reference_date": REFERENCE_DATE.strftime("%Y-%m-%d"),
        "projects": dashboard_projects,
        "updates": updates,
        "notifications": notifications,
        "summary": {
            "projects_total": len(projects),
            "projects_completed": sum(
                project["status"] == "concluído" for project in projects
            ),
            "new_responses": len(updates),
            "notifications_pending": len(notifications),
            "low_nps": sum(
                update["nps"] is not None and update["nps"] <= 6
                for update in updates
            ),
            "in_progress": sum(project["queue"] == "in_progress" for project in projects),
            "waiting": sum(project["queue"] == "waiting" for project in projects),
            "action_required": sum(
                project["queue"] == "action_required" for project in projects
            ),
        },
    }
