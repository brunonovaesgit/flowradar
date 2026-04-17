# FlowRadar

> Seu time não é lento.  
> Seu fluxo está preso.

---

A maioria das organizações mede velocidade.

- Lead time  
- Throughput  
- WIP  

E mesmo assim… continuam lentas.

O problema não está nessas métricas.

Está no que elas **não mostram**.

---

## 🧠 O problema invisível

Times não trabalham isolados.

Eles dependem uns dos outros.

E essas dependências:

- criam filas invisíveis  
- espalham atraso pelo sistema  
- distorcem métricas  
- tornam previsões inúteis  

Você não tem um problema de execução.

Você tem um problema de **estrutura de fluxo**.

---

## 🔍 O que o FlowRadar faz

O FlowRadar trata sua organização como ela realmente funciona:

> uma rede de dependências

Ele permite:

- mapear quem depende de quem  
- identificar gargalos sistêmicos  
- medir impacto estrutural (não só esforço)  
- simular mudanças antes de aplicá-las  
- visualizar o fluxo de forma objetiva  

---

## ⚙️ Como funciona (em alto nível)

1. Você fornece dados de trabalho (issues, dependências, fluxos)
2. O FlowRadar constrói uma rede
3. Aplica métricas de rede (centralidade, impacto, fragilidade)
4. Gera análises e simulações

---

## 🚀 Instalação

### 1. Clone do repositório 

```bash
git clone https://github.com/brunonovaesgit/flowradar.git
cd flowradar
```

> Antes de rodar o clone, escolha a pasta onde você quer salvar o projeto localmente.

---

### 2. Ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux / Mac

# ou
venv\Scripts\activate     # Windows
```

---

### 3. Dependências
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

---

▶️ Execução

Rodar análise principal:
```bash
python run_flowradar.py
```

Simulações de impacto: 
```bash
python compare_simulations.py
```

---

🧪 Testes

Rodar todos os testes:
```bash
pytest
```

Rodar com mais detalhes: 
```bash
pytest -vv
```

📊 O que você recebe

Dependendo do cenário, o FlowRadar gera:

rede de dependências (graph.json)
ranking de impacto (quem realmente importa no fluxo)
heatmaps de concentração de dependências
simulações de remoção ou alteração de squads
explicações estruturais do comportamento do sistema

---

📈 O que você começa a enxergar

Depois de usar o FlowRadar, algumas coisas ficam óbvias:

por que features ficam presas por semanas
por que dividir histórias nem sempre resolve
por que alguns times “sempre atrasam”
por que métricas boas não significam fluxo saudável

---

⚠️ O desconforto necessário

O FlowRadar não vai te dar respostas confortáveis.

Ele pode mostrar que:

o problema não é o time
o problema não é o processo
o problema é a forma como o trabalho está organizado

---

📊 Estrutura do projeto

```bash
.
├── src/
│   ├── analysis/
│   ├── graph_builder/
│   ├── metrics/
│   ├── pipeline/
│   ├── reports/
│   ├── simulations/
│   └── visualizations/
│
├── tests/
├── data/
│
├── run_flowradar.py
├── compare_simulations.py
│
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
└── README.md
```

🧠 Para quem é
Agile Coaches que já perceberam que métricas não bastam
Líderes de produto lidando com dependências entre squads
Arquitetos organizacionais
Times que vivem bloqueios constantes sem explicação clara


🧩 O que vem pela frente
Explorer visual da rede (interativo)
Simulações mais avançadas
Análise preditiva de gargalos
Integração direta com ferramentas (Jira, etc.)


👤 Autor
Bruno Novaes (brunonovaes@gmail.com)

Trabalhando na interseção entre:
- fluxo de trabalho
- estruturas organizacionais
- sistemas complexos


⭐ Se isso fez sentido para você

Deixe uma estrela no repositório.
Isso ajuda o projeto a evoluir — e mais pessoas a enxergarem o problema que ninguém está olhando.


📄 Licença

MIT

---

# As 5 métricas oficiais do FlowRadar

Essas cinco já são suficientes para você ter um modelo sólido, consistente e explicável.

1. 🔥 System Impact Score (SIS)
📌 O que é

Mede o quanto um nó (squad, sistema, etapa) impacta o fluxo como um todo.

🧮 Como calcular (base)

Use centralidade:

PageRank (recomendado)
```bash
SIS = pagerank(node)
```

🧠 Interpretação
- alto SIS → esse nó influencia grande parte do sistema
- baixo SIS → impacto local


2. ⚠️ Flow Fragility Index (FFI)
📌 O que é

Mede o quanto o sistema depende de poucos nós críticos.

🧮 Como calcular
```bash
FFI = soma_dos_top_N_SIS / soma_total_SIS
```

Exemplo:
- pegue top 20% dos nós mais críticos
- veja quanto do impacto total eles concentram

🧠 Interpretação
- alto FFI → sistema frágil (concentrado)
- baixo FFI → sistema distribuído (resiliente)


3. 🔗 Dependency Load Score (DLS)
📌 O que é

Mede a carga de dependências de um nó.

🧮 Como calcular
```bash
DLS = in_degree + out_degree
```

Ou ponderado:
```bash
DLS = dependencias_entrada * peso + dependencias_saida
```

🧠 Interpretação
- alto DLS → potencial gargalo
- baixo DLS → fluxo mais simples


4. 🚧 Flow Bottleneck Probability (FBP)
📌 O que é

Probabilidade de um nó se tornar gargalo.

🧮 Como calcular (modelo simples)
```bash
FBP = normalizar(SIS * DLS)
```

Ou mais refinado:
```bash
FBP = (SIS * DLS) / capacidade_do_nó
```

🧠 Interpretação
- alto FBP → risco real de travar o fluxo
- baixo FBP → baixo risco


5. 🧩 Coordination Cost Index (CCI)
📌 O que é

Custo estrutural de coordenação do sistema.

🧮 Como calcular
```bash
CCI = total_de_arestas / total_de_nós
```

Ou:
```bash
CCI = média_de_dependências_por_nó
```

🧠 Interpretação
alto CCI → sistema complexo, difícil de coordenar
baixo CCI → sistema simples


🧭 Como essas métricas se conectam
```bash
--------------------------------------------
|   Métrica     Responde                   |
-------------------------------------------|
|   SIS	        Quem importa no sistema    |
|   FFI	        O sistema é frágil?        |
|   DLS	        Quem está sobrecarregado   |
|   FBP	        Onde vai travar            |
|   CCI	        Quão complexo é coordenar  |
--------------------------------------------
```

🔥 Exemplo real (como você usaria)

Você olha o resultado e diz:
- Squad A → alto SIS → crítico
- Squad B → alto DLS → sobrecarregado
- Squad C → alto FBP → próximo gargalo
- Sistema → alto FFI → frágil
- Sistema → alto CCI → difícil de operar

👉 Isso vira narrativa executiva.

---

⚠️ Regras importantes (pra não virar buzzword)
1. Toda métrica precisa:
    - ter cálculo simples
    - ser explicável em 1 frase
    - gerar ação
2. Evite criar 10+ métricas
    → essas 5 já são fortes
3. Prefira consistência > sofisticação