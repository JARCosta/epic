const reference = document.getElementById('reference');
const summary = document.getElementById('summary');
const projectsTable = document.getElementById('projects');
const updatesTable = document.getElementById('updates');
const notificationsTable = document.getElementById('notifications');
const queueFilter = document.getElementById('queue-filter');
let projects = [];

function emptyRow(table, message, columnCount) {
  const row = document.createElement('tr');
  const value = cell(message);
  value.colSpan = columnCount;
  row.append(value);
  table.append(row);
}

function cell(value, className = '') {
  const element = document.createElement('td');
  element.textContent = value ?? '—';
  if (className) element.className = className;
  return element;
}

function renderSummary(values) {
  const cards = [
    ['Projetos', values.projects_total],
    ['Em curso', values.in_progress],
    ['Ação necessária', values.action_required],
    ['A aguardar', values.waiting],
    ['Novas respostas', values.new_responses],
    ['NPS baixo', values.low_nps],
  ];
  summary.replaceChildren(...cards.map(([label, value]) => {
    const card = document.createElement('div');
    card.className = 'card';
    card.textContent = label;
    const strong = document.createElement('strong');
    strong.textContent = value;
    card.append(strong);
    return card;
  }));
}

function renderProjects() {
  const selected = queueFilter.value;
  projectsTable.replaceChildren();
  const filteredProjects = projects.filter((item) => selected === 'all' || item.queue === selected);
  if (!filteredProjects.length) {
    emptyRow(projectsTable, 'Não existem projetos nesta fila.', 6);
    return;
  }
  for (const project of filteredProjects) {
    const row = document.createElement('tr');
    const pending = project.pending_actions?.length
      ? ` Pendentes: ${project.pending_actions.join(', ')}`
      : '';
    row.append(
      cell(project.id),
      cell(project.status),
      cell(`${project.area} / ${project.client}`),
      cell(`${project.project_manager} (${project.manager_email || 'email em falta'})`),
      cell(project.last_action_date),
      cell(`${project.task}.${pending}`, project.queue === 'action_required' ? 'warning' : ''),
    );
    projectsTable.append(row);
  }
}

async function loadSnapshot() {
  const response = await fetch('/api/snapshot');
  if (!response.ok) throw new Error('Não foi possível carregar o dashboard.');
  const snapshot = await response.json();
  reference.textContent = `Data de referência: ${snapshot.reference_date}`;
  projects = snapshot.projects;
  renderSummary(snapshot.summary);
  renderProjects();

  updatesTable.replaceChildren();
  if (!snapshot.updates.length) emptyRow(updatesTable, 'Não existem atualizações.', 5);
  for (const update of snapshot.updates) {
    const row = document.createElement('tr');
    const observation = update.nps !== null && update.nps <= 6 ? 'NPS baixo: requer alerta' : 'Sem projeto/responsável no ficheiro DEMO';
    row.append(cell(update.response_id), cell(update.nps, update.nps !== null && update.nps <= 6 ? 'warning' : ''), cell('Não identificado'), cell('Não identificado'), cell(observation));
    updatesTable.append(row);
  }
  notificationsTable.replaceChildren();
  if (!snapshot.notifications.length) emptyRow(notificationsTable, 'Não existem notificações.', 4);
  for (const notification of snapshot.notifications) {
    const row = document.createElement('tr');
    row.append(cell(notification.response_id), cell(notification.type), cell(notification.reasons.join('; ')), cell(notification.status));
    notificationsTable.append(row);
  }
}

queueFilter.addEventListener('change', renderProjects);
loadSnapshot().catch((error) => {
  reference.textContent = error.message;
  emptyRow(projectsTable, 'Erro ao carregar projetos.', 6);
  emptyRow(updatesTable, 'Erro ao carregar respostas.', 5);
  emptyRow(notificationsTable, 'Erro ao carregar notificações.', 4);
});
