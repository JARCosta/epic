# GOAL --- Sistema de Voz do Cliente (VoC)

## 1. Objetivo do projeto

Construir iterativamente um protótipo funcional de um sistema de **Voz
do Cliente (VoC)** que automatize o ciclo de satisfação dos projetos:

**deteção de conclusão → identificação do gestor → convite por email →
lembretes → receção/tratamento das respostas → dashboard por área →
alerta e escalada de insatisfação.**

O sistema deve aceitar os ficheiros Excel fornecidos como inputs,
interpretar os dados e as regras de negócio neles contidos, validar a
qualidade dos dados e evoluir por iterações até cumprir os entregáveis e
critérios de aceitação deste documento.

O protótipo trabalha sobre os exports fornecidos. Não deve assumir
acesso autenticado aos sistemas reais GTraining ou Impulsa/LimeSurvey.

## 2. Contexto e problema

-   O questionário de satisfação já existe nos vários serviços.
-   O envio manual é irregular e depende da memória de cada gestor.
-   Cada `ID_Projeto` pode ter várias ações, registadas no GTraining.
-   O questionário deve ser enviado no fim do projeto, **depois da
    última ação**.
-   As respostas chegam à Impulsa (LimeSurvey) e devem ficar visíveis
    num dashboard por área.
-   Deve existir um alerta quando um cliente está insatisfeito, com
    escalada para o gestor adequado.

Os dados do exercício são anonimizados e foram alterados. Não
representam clientes reais.

## 3. Inputs esperados

O utilizador deve conseguir carregar os ficheiros Excel disponibilizados
para o exercício. O conjunto referido no enunciado inclui:

1.  **Regras de negócio (R1--R11)** --- fonte de verdade para
    elegibilidade, prazos, exclusões, lembretes, estados e restantes
    decisões operacionais.
2.  **Export de ações do GTraining** --- ações de setembro a dezembro de
    2026.
3.  **Emails dos gestores de projeto** --- correspondência entre
    projetos/gestores e endereços de email.
4.  **Questionário** --- estrutura das perguntas, escalas e dimensões
    avaliadas.
5.  **Respostas da Impulsa/LimeSurvey** --- respostas submetidas pelos
    clientes.
6.  **Feriados** --- calendário relevante para cálculo de dias úteis e
    agendamento, conforme as regras R1--R11.

### 3.1 Requisitos de ingestão

-   Aceitar ficheiros `.xlsx` e, se viável, `.xls` e `.csv`.
-   Permitir carregar vários ficheiros numa execução.
-   Permitir indicar ou confirmar a função de cada ficheiro, caso não
    seja possível identificá-la automaticamente.
-   Inspecionar nomes de folhas, cabeçalhos, tipos de dados, linhas
    vazias, duplicados e valores em falta.
-   Não assumir que os nomes das folhas ou colunas são sempre iguais:
    detetar variações e pedir confirmação quando a correspondência for
    ambígua.
-   Preservar os ficheiros originais; todas as transformações devem
    ocorrer em cópias ou em memória.
-   Registar nome do ficheiro, data/hora de carregamento, folhas lidas,
    linhas processadas, erros e avisos.
-   Apresentar um resumo de validação antes de executar cálculos ou
    gerar envios.
-   Permitir substituir um ficheiro e voltar a processar sem duplicar
    convites, lembretes ou respostas.

### 3.2 Contrato de dados

Criar um mapeamento explícito entre as colunas reais dos Excel e os
campos lógicos usados pelo sistema. No mínimo, procurar identificar:

-   `ID_Projeto`
-   identificador da ação
-   data da ação
-   estado da ação, se existir
-   gestor do projeto
-   email do gestor
-   área/serviço
-   campos de identificação da resposta
-   respostas às perguntas do questionário
-   datas de resposta/submissão
-   feriados e respetivas datas

Esta lista é um conjunto de campos a procurar, não uma afirmação de que
todos existem com estes nomes. O sistema deve confirmar a estrutura
efetiva dos ficheiros. Não inventar colunas, valores ou relações que não
estejam sustentados pelos dados ou pelas regras.

## 4. Requisitos funcionais

### RF-01 --- Leitura e validação dos dados

1.  Ler o export de ações do GTraining.
2.  Ler os restantes ficheiros Excel.
3.  Identificar a função de cada ficheiro e folha.
4.  Validar campos obrigatórios, tipos, datas, identificadores e
    relações.
5.  Detetar duplicados, registos incompletos, inconsistências e valores
    inválidos.
6.  Produzir um relatório de qualidade dos dados, com erros bloqueantes
    e avisos não bloqueantes.
7.  Permitir corrigir o mapeamento ou substituir ficheiros e repetir a
    validação.

### RF-02 --- Determinação dos projetos elegíveis

1.  Agrupar as ações por `ID_Projeto`.
2.  Determinar a última ação de cada projeto, segundo as regras R1--R11.
3.  Identificar projetos concluídos e elegíveis à data de referência.
4.  Aplicar rigorosamente as regras de negócio, incluindo eventuais
    exclusões, períodos de espera, dias úteis, feriados e condições
    especiais.
5.  Evitar o envio antes da última ação do projeto.
6.  Distinguir projetos elegíveis, ainda não elegíveis, já contactados e
    casos que exigem revisão humana.
7.  Gerar uma justificação rastreável para a decisão de cada projeto.

**Data de referência do entregável:** 12/11/2026.

A data de referência deve ser configurável. Não usar a data atual do
computador como substituto silencioso da data de referência do
exercício.

### RF-03 --- Associação ao gestor e preparação dos envios

1.  Associar cada projeto elegível ao gestor correto.
2.  Obter o endereço de email a partir do ficheiro de gestores.
3.  Detetar gestores ou emails em falta, múltiplas correspondências e
    associações ambíguas.
4.  Preparar um convite por projeto, de acordo com o questionário e com
    as regras.
5.  Gerar uma lista de envios com, no mínimo, projeto, ação/última ação,
    destinatário e data prevista.
6.  Gerar uma lista separada de exceções para revisão humana.
7.  Não enviar mensagens reais sem autorização explícita e sem
    integração de email configurada.

### RF-04 --- Sequência de comunicação

Implementar ou simular o ciclo de comunicação definido nas regras
R1--R11:

-   convite inicial;
-   controlo do estado de resposta;
-   lembretes, nos prazos e condições definidos;
-   encerramento do ciclo;
-   prevenção de mensagens duplicadas;
-   registo de cada evento de comunicação.

Preparar modelos de email para: - convite ao preenchimento do
questionário; - lembrete.

Os modelos devem usar campos dinâmicos quando suportados pelos dados,
por exemplo projeto, destinatário, ligação ao questionário e prazo. Não
inventar uma ligação real à Impulsa: usar configuração ou placeholder
claramente identificado.

### RF-05 --- Tratamento das respostas da Impulsa

1.  Ler e normalizar as respostas exportadas da Impulsa/LimeSurvey.
2.  Interpretar escalas e dimensões com base no questionário fornecido.
3.  Validar respostas incompletas, inválidas ou fora da escala.
4.  Normalizar a área/serviço de acordo com as correspondências
    confirmadas.
5.  Identificar respostas repetidas ou potencialmente duplicadas.
6.  Relacionar respostas com projetos sempre que exista uma chave
    fiável.
7.  Colocar correspondências incertas em revisão humana; não associar
    por aproximação sem registar essa incerteza.
8.  Preservar comentários textuais, tratando-os como conteúdo
    potencialmente sensível e apresentando-os apenas aos utilizadores
    autorizados.

### RF-06 --- Dashboard por área

Criar um dashboard que se atualize quando são importadas novas
respostas. Deve apresentar, no mínimo:

-   número de respostas;
-   NPS, se o questionário e os dados permitirem calculá-lo;
-   resultados por dimensão;
-   resultados por área/serviço;
-   evolução temporal, quando existirem datas suficientes;
-   alertas de insatisfação;
-   comentários dos clientes, quando disponíveis.

Documentar a fórmula usada para cada indicador. Não calcular NPS se a
escala/pergunta necessária não estiver presente ou não corresponder à
definição aplicável; nesse caso, explicar a limitação.

O dashboard deve permitir filtrar por área e, quando suportado pelos
dados, por período e outros atributos relevantes.

### RF-07 --- Alertas e escalada

1.  Detetar insatisfação segundo os limiares e condições definidos nas
    regras R1--R11.
2.  Criar um alerta associado à resposta, projeto e área, quando
    possível.
3.  Identificar o destinatário da escalada conforme as regras e os dados
    disponíveis.
4.  Registar estado, data, motivo e histórico do alerta.
5.  Distinguir alertas novos, em tratamento e resolvidos, se esse fluxo
    estiver definido ou for aprovado.
6.  Quando não for possível identificar o responsável, criar uma exceção
    para revisão humana.

Não inventar limiares de insatisfação nem destinatários de escalada. Se
as regras não forem explícitas, apresentar a lacuna e pedir decisão ao
utilizador.

### RF-08 --- Automação ponta a ponta

Desenhar uma proposta de arquitetura com:

-   gatilho de deteção de projetos concluídos;
-   processamento e validação dos exports;
-   associação ao gestor;
-   geração e envio de convites;
-   agendamento e controlo de lembretes;
-   integração com Impulsa/LimeSurvey;
-   atualização do dashboard;
-   geração e encaminhamento de alertas;
-   logs, auditoria, tratamento de erros e reprocessamento.

Distinguir claramente: - **protótipo executável com os ficheiros
fornecidos**; - **integrações propostas para produção**; - **integrações
que dependem de credenciais, APIs ou permissões externas**.

O enunciado indica que GTraining e Impulsa exigem password. O protótipo
deve, por isso, funcionar com os exports fornecidos, sem fingir que está
ligado aos sistemas reais.

## 5. Entregáveis obrigatórios

O projeto deve produzir:

### E-01 --- Mapa do sistema

Um diagrama ou descrição do fluxo:

`deteção → envio → lembretes → resposta na Impulsa → dashboard → alerta`

Incluir sistemas, dados de entrada/saída, gatilhos, decisões, exceções e
pontos que exigem intervenção humana.

### E-02 --- Lista de envios a 12/11/2026

Uma tabela com: - projeto; - ação/última ação relevante; -
destinatário; - email; - data de envio ou data prevista; - estado de
elegibilidade; - justificação da decisão.

Separar os casos que não podem ser processados automaticamente.

### E-03 --- Lista de exceções para revisão humana

Para cada exceção, indicar: - identificador do projeto/resposta, se
disponível; - tipo de problema; - dados em falta ou contraditórios; -
impacto no processamento; - ação recomendada para resolução.

### E-04 --- Dashboard por área

Dashboard funcional com: - respostas; - NPS, quando calculável; -
dimensões; - alertas; - comentários; - filtros e atualização após
importação de novas respostas.

### E-05 --- Modelos de email

-   convite;
-   lembrete.

Incluir assunto, corpo e variáveis dinâmicas. Assinalar placeholders que
dependem de configuração externa.

### E-06 --- Stack tecnológica e indicadores de sucesso

Documentar: - tecnologias e bibliotecas escolhidas; - arquitetura e
componentes; - estratégia de armazenamento; - método de atualização do
dashboard; - integrações e dependências externas; - segurança e controlo
de acesso; - indicadores de sucesso mensuráveis.

Os indicadores devem ser propostos e identificados como propostas, não
como metas fornecidas pelo enunciado. Exemplos a avaliar: percentagem de
projetos elegíveis detetados corretamente, taxa de associação correta ao
gestor, taxa de duplicação de convites, tempo entre conclusão e convite,
taxa de resposta e tempo de tratamento de alertas.

## 6. Regras de negócio e precedência

As regras R1--R11 existentes no Excel são a fonte de verdade para o
comportamento operacional.

O LLM/agente de desenvolvimento deve:

1.  Extrair as regras R1--R11 dos ficheiros fornecidos.
2.  Preservar o identificador de cada regra.
3.  Converter cada regra numa condição verificável e, quando possível,
    num teste automatizado.
4.  Manter uma matriz `regra → implementação → teste → resultado`.
5.  Assinalar regras contraditórias, incompletas ou ambíguas.
6.  Pedir esclarecimento antes de implementar decisões de negócio
    ambíguas.
7.  Nunca substituir silenciosamente uma regra do Excel por uma
    suposição ou prática genérica.

Quando uma decisão não estiver coberta pelo enunciado nem pelos Excel,
classificá-la como: - decisão técnica proposta; ou - decisão de negócio
pendente.

## 7. Desenvolvimento iterativo obrigatório

O projeto deve ser desenvolvido por etapas pequenas, verificáveis e
cumulativas. Não tentar construir tudo numa única passagem.

### Iteração 0 --- Descoberta e inventário

-   Listar os ficheiros recebidos.
-   Inspecionar folhas, colunas, dimensões e amostras de dados.
-   Identificar as regras R1--R11.
-   Identificar o questionário, escalas e estrutura das respostas.
-   Produzir um dicionário de dados e um relatório de ambiguidades.
-   Não avançar para decisões de negócio não confirmadas.

**Saída:** inventário dos inputs, dicionário de dados, matriz de regras
e lista de questões em aberto.

### Iteração 1 --- Ingestão e qualidade dos dados

-   Implementar carregamento dos Excel.
-   Implementar mapeamento de colunas.
-   Implementar validações e relatório de qualidade.
-   Testar ficheiros válidos, incompletos, duplicados e com formatos
    inesperados.

**Critério de conclusão:** todos os ficheiros são lidos ou os erros são
explicados de forma acionável; nenhum erro é ocultado.

### Iteração 2 --- Elegibilidade e envios

-   Implementar agrupamento por projeto e cálculo da última ação.
-   Implementar regras R1--R11 relativas à elegibilidade e calendário.
-   Associar gestores e emails.
-   Produzir a lista de envios de 12/11/2026 e as exceções.
-   Testar casos-limite e prevenção de duplicados.

**Critério de conclusão:** cada projeto tem uma decisão explicável e
rastreável.

### Iteração 3 --- Comunicação

-   Criar modelos de convite e lembrete.
-   Implementar máquina de estados do ciclo de comunicação.
-   Simular envios e lembretes.
-   Registar eventos e impedir envios repetidos.
-   Só ativar envio real após autorização e configuração explícitas.

**Critério de conclusão:** é possível demonstrar o ciclo completo sem
contactar destinatários reais.

### Iteração 4 --- Respostas e indicadores

-   Importar respostas da Impulsa.
-   Normalizar escalas, áreas e dimensões.
-   Tratar inválidas e duplicadas.
-   Calcular indicadores suportados pelo questionário.
-   Criar testes para os cálculos.

**Critério de conclusão:** os resultados são reproduzíveis e cada
indicador tem fórmula documentada.

### Iteração 5 --- Dashboard e alertas

-   Criar dashboard por área.
-   Atualizar indicadores após nova importação.
-   Implementar alertas conforme as regras confirmadas.
-   Implementar escalada ou simulação de escalada.
-   Disponibilizar comentários e filtros com as devidas restrições.

**Critério de conclusão:** uma nova resposta importada reflete-se no
dashboard e gera alerta quando satisfaz as condições definidas.

### Iteração 6 --- Arquitetura e entrega

-   Documentar mapa ponta a ponta.
-   Documentar stack, integrações e limitações.
-   Consolidar entregáveis E-01 a E-06.
-   Executar testes de regressão.
-   Produzir instruções de instalação, configuração e execução.

**Critério de conclusão:** outra pessoa consegue executar o protótipo a
partir dos ficheiros e instruções entregues.

## 8. Protocolo de trabalho do LLM

Em cada iteração, o LLM deve seguir este ciclo:

1.  **Inspecionar:** verificar os ficheiros, código e artefactos
    existentes antes de alterar.
2.  **Planear:** indicar o objetivo da iteração, ficheiros a
    criar/alterar e critérios de aceitação.
3.  **Identificar dependências:** explicitar dados, regras ou decisões
    em falta.
4.  **Implementar:** fazer alterações pequenas e coerentes.
5.  **Testar:** executar testes e validações relevantes.
6.  **Comparar:** verificar os resultados contra as regras e critérios
    de aceitação.
7.  **Documentar:** atualizar README, dicionário de dados, matriz de
    regras e registo de decisões.
8.  **Reportar:** resumir o que foi concluído, evidências, problemas,
    limitações e próximo passo.

No final de cada iteração, parar e apresentar o resultado para validação
do utilizador antes de avançar para decisões irreversíveis ou para a
iteração seguinte. Pode prosseguir automaticamente em tarefas técnicas
de baixo risco que não alterem regras de negócio nem provoquem
comunicações externas.

### Regras de execução

-   Não apagar nem sobrescrever os ficheiros de input.
-   Não enviar emails reais, contactar clientes ou alterar sistemas
    externos sem autorização explícita.
-   Não inventar dados, regras, destinatários, limiares ou resultados.
-   Não descartar linhas inválidas sem as contabilizar e explicar.
-   Tornar os processos repetíveis e idempotentes: reimportar os mesmos
    ficheiros não deve criar envios ou respostas duplicadas.
-   Manter logs e rastreabilidade das transformações.
-   Separar dados brutos, dados normalizados e resultados calculados.
-   Usar configuração para datas de referência, caminhos, limiares e
    integrações.
-   Proteger emails e comentários; não os expor desnecessariamente.
-   Incluir testes automatizados para regras de negócio, cálculos e
    casos-limite.
-   Se faltar informação essencial, fazer uma pergunta objetiva em vez
    de adivinhar.

## 9. Critérios globais de aceitação

O projeto só está concluído quando:

-   [ ] Os ficheiros Excel podem ser carregados e validados.
-   [ ] O sistema identifica e documenta as regras R1--R11.
-   [ ] A última ação de cada projeto é determinada corretamente.
-   [ ] A elegibilidade à data de referência é calculada segundo as
    regras.
-   [ ] Cada projeto elegível é associado ao gestor correto ou
    encaminhado para exceção.
-   [ ] A lista de envios de 12/11/2026 é produzida.
-   [ ] Os convites e lembretes podem ser gerados e simulados.
-   [ ] As respostas da Impulsa são limpas e normalizadas.
-   [ ] Os indicadores são calculados apenas quando os dados os
    suportam.
-   [ ] O dashboard apresenta resultados por área e atualiza após novas
    importações.
-   [ ] Os alertas respeitam as regras de insatisfação e têm
    rastreabilidade.
-   [ ] Existe uma lista de exceções para revisão humana.
-   [ ] O mapa do sistema, a stack e os indicadores de sucesso estão
    documentados.
-   [ ] Existe documentação suficiente para instalar e executar o
    protótipo.

## 10. Limites e pressupostos explícitos

-   A data de referência do entregável é **12/11/2026**.
-   O export de ações indicado cobre **setembro a dezembro de 2026**.
-   Os sistemas reais GTraining e Impulsa exigem password.
-   O protótipo deve operar sobre os exports fornecidos.
-   O enunciado não especifica, por si só, os detalhes das regras
    R1--R11, os limiares de insatisfação, as fórmulas do questionário,
    os campos concretos dos Excel ou os endpoints de API. Estes
    elementos devem ser extraídos dos ficheiros correspondentes ou
    assinalados como pendentes.
-   A duração de 30 minutos indicada no enunciado é contexto do
    exercício; não deve ser interpretada como requisito de execução do
    software.

## 11. Primeira instrução ao agente

Começa pela **Iteração 0 --- Descoberta e inventário**. Analisa todos os
Excel disponibilizados, sem modificar os originais. Apresenta:

1.  lista dos ficheiros e folhas encontrados;
2.  colunas e tipos de dados detetados;
3.  identificação das folhas que contêm as regras R1--R11;
4.  dicionário de dados preliminar;
5.  problemas de qualidade e ambiguidades;
6.  plano de implementação priorizado.

Não implementes ainda regras ambíguas. Aguarda validação das decisões de
negócio em falta e, depois, executa as iterações pela ordem definida.
