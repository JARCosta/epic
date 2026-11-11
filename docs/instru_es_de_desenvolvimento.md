# Guia de Desenvolvimento: Desafio 1 - Voz do Cliente

## 📌 Contexto & Objetivo
Construir uma solução automatizada de ponta a ponta que:
1. Identifique projetos concluídos no sistema **GTraining** (data de referência: **12/11/2026**).
2. Associe os projetos concluídos aos respetivos **Gestores de Projeto**.
3. Gerencie o ciclo de comunicação por e-mail (convites, lembretes, fechos e exceções para revisão humana).
4. Processe e limpe as respostas de satisfação recebidas via **Impulsa / LimeSurvey** (tratamento de escalas, áreas e respostas inválidas).
5. Alimente um **Dashboard por Área** com atualização em tempo real (NPS, dimensões de análise, alertas de insatisfação).
6. Implemente um sistema de **Alerta e Escalada** para Gestores de Cliente quando a insatisfação for detetada.

---

## 🛠️ Entregáveis Esperados
- [ ] **Mapa do Sistema (Arquitetura & Fluxo):** Deteção $\rightarrow$ Envio $\rightarrow$ Lembretes $\rightarrow$ Resposta na Impulsa $\rightarrow$ Dashboard $\rightarrow$ Alerta.
- [ ] **Lista de Envios a 12/11/2026:** Ficheiro/Tabela com Ação, Destinatário, Data prevista e Lista de Exceções para revisão humana.
- [ ] **Dashboard por Área:** Respostas, NPS por área, dimensões analisadas, alertas de insatisfação e comentários dos clientes.
- [ ] **Modelos de E-mail (Templates):** Convite para questionário e Lembretes.
- [ ] **Proposta de Stack Tecnológica & KPIs:** Definição de gatilhos, integrações (APIs LimeSurvey/GTraining) e indicadores de sucesso.

---

## 🚀 Passo a Passo (Step-by-Step) & Cuidados Essenciais

### PASSO 1: Ingestão e Validação de Dados (Dataset Principal)
**Ficheiro:** `Desafio1_Dataset_Participantes.xlsx`

* **Ações a Realizar:**
  1. Carregar as abas com o export das ações do GTraining (set.-dez. 2026), mapa de Gestores, Regras de Negócio (R1 a R11) e Feriados.
  2. Implementar a lógica de apuramento da data final do projeto:
     - Um projeto (`ID_Projeto`) é composto por várias ações.
     - A data de conclusão do projeto é a **data de fim da ÚLTIMA ação** do respetivo projeto.
  3. Filtrar os projetos elegíveis para envio à data de referência (**12/11/2026**).

⚠️ **Cuidados a Ter neste Passo:**
- **Feriados e Fins de Semana:** Validar se os prazos de lembretes ou datas de envio dependem de dias úteis (consultar aba de Feriados e R1-R11).
- **Projetos Incompletos vs. Concluídos:** Não disparar questionário para projetos onde ainda existam ações pendentes/futuras após 12/11/2026.
- **Limpeza de Chaves:** Garantir correlação exata entre `ID_Projeto`, Gestor de Projeto e Gestor de Cliente (atenção a *whitespaces* ou inconsistências nos IDs).

---

### PASSO 2: Tratamento de Exceções e Regras de Negócio (R1 a R11)

* **Ações a Realizar:**
  1. Mapear todas as regras de negócio R1 a R11 definidas no dataset.
  2. Criar o pipeline para gerar a **Lista de Envios a 12/11/2026**.
  3. Criar uma **Lista de Exceções para Revisão Humana** para casos não elegíveis ou duvidosos.

⚠️ **Cuidados a Ter neste Passo:**
- **Filtros de Exceção:** Identificar explicitamente por que motivo um registo vai para a "Lista de Exceções" (ex.: e-mail em falta, projeto cancelado, regra de cadência de contacto violada).
- **Consistência temporal:** Respeitar a data fixa de simulação (**12/11/2026**).

---

### PASSO 3: Ingestão e Limpeza de Respostas (Impulsa / LimeSurvey)
**Ficheiros:** `Desafio1_Dataset_Participantes.xlsx` (Respostas) + `Desafio1_Respostas_Novas_DEMO_JURI.xlsx` (Dados de Teste)

* **Ações a Realizar:**
  1. Ler as respostas do questionário e aplicar as seguintes transformações:
     - Normalização/padronização de escalas (ex.: converter escalas numéricas ou ordinais para cálculo uniforme do NPS).
     - Associação de cada resposta à respetiva **Área de Negócio**.
     - Identificação e filtragem de respostas **inválidas/duplicadas/incompletas**.
  2. Testar o pipeline de ingestão utilizando os dados de teste do ficheiro `Desafio1_Respostas_Novas_DEMO_JURI.xlsx`.

⚠️ **Cuidados a Ter neste Passo:**
- **Cálculo de NPS:** Garantir a fórmula correta do Net Promoter Score:
  $$\text{NPS} = \% \text{Promotores (9-10)} - \% \text{Detratores (0-6)}$$
- **Validação de Inputs de Teste:** O script de ingestão deve processar novos dados no mesmo formato do ficheiro do Júri sem quebrar.

---

### PASSO 4: Módulo de Comunicação & Templates de E-mail

* **Ações a Realizar:**
  1. Desenhar a sequência temporal de comunicação:
     - **T0:** Convite inicial pós-conclusão.
     - **T+N:** Lembretes (conforme regras R1-R11).
     - **T+X:** Fecho de processo/expiração do link.
  2. Criar os modelos de e-mail (HTML/Markdown):
     - Template de **Convite**.
     - Template de **Lembrete**.
     - Template de **Alerta Interno de Insatisfação**.

⚠️ **Cuidados a Ter neste Passo:**
- **Tom de Voz:** Empático, profissional e alinhado com a marca Impulsa/EpicTalent Society.
- **Campos Dinâmicos (Placeholders):** Garantir suporte a tags dinâmicas como `{Nome_Gestor}`, `{Nome_Projeto}`, `{Data_Fim}`, `{Link_Questionario}`.

---

### PASSO 5: Dashboard por Área & Sistema de Alerta

* **Ações a Realizar:**
  1. Construir uma interface ou componente de visualização de dados com as métricas essenciais:
     - Volume total de respostas e taxa de resposta.
     - **NPS global e desagregado por Área**.
     - Análise por dimensões (ex.: Conteúdo, Formador, Aplicabilidade).
     - Feed de comentários e sugestões dos clientes.
  2. Implementar a regra de **Alerta e Escalada**:
     - Quando o feedback/score atingir um limiar de insatisfação (ex.: Detrator com rating $\le 6$), gerar um alerta imediato destinado ao **Gestor de Cliente**.

⚠️ **Cuidados a Ter neste Passo:**
- **Atualização Automática:** O dashboard deve reagir a novas entradas (simuladas via lote do Júri).
- **Fácil Leitura Visual:** Destacar claramente clientes insatisfeitos para permitirem ação rápida de retenção/recuperação.

---

### PASSO 6: Definição da Arquitetura de Automação & Documentação

* **Ações a Realizar:**
  1. Escrever a proposta da **Stack Tecnológica**:
     - **Triggers:** Webhooks / Agendadores (Cron).
     - **Integrações:** APIs REST para GTraining e LimeSurvey (Impulsa).
     - **Database/Warehouse:** Onde armazenar logs de envios, respostas e estados dos projetos.
  2. Definir os **KPIs e Indicadores de Sucesso** do sistema automatizado (ex.: Taxa de Resposta, Tempo Médio de Resolução de Alertas de Insatisfação, Redução do Trabalho Manual).

---

## 📊 Matriz de Checklist dos Entregáveis

| Entregável | Requisito Principal | Ficheiro/Fase |
| :--- | :--- | :--- |
| **Mapa do Fluxo** | Diagrama lógico de integração e estados | Relatório |
| **Lista 12/11/2026** | Projetos elegíveis, datas e e-mails mapeados | Output tabular / Script |
| **Lista de Exceções** | Projetos retidos com justificativa | Output tabular / Script |
| **Dashboard** | NPS por área, alertas, gráficos, comentários | Aplicação/Script |
| **Templates E-mail** | Textos para Convite e Lembretes com placeholders | Ficheiros de texto / HTML |
| **Proposta Stack** | Detalhe de triggers, APIs e KPIs de sucesso | Relatório |