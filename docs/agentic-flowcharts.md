# Agentic workflow — flowcharts

Two high-level views. Solid arrow = runs/writes · dashed arrow = reads only.

Config: [`agentic-flow.yaml`](../agentic-flow.yaml) · Artifacts: [`ARTIFACTS.md`](working/ARTIFACTS.md)

## Legend

| Color | Layer |
|-------|--------|
| Pink | User |
| Blue | Agent |
| Amber | Rules — `docs/rules/` |
| Green | Context — `docs/context/` |
| Purple | Index — `graph.db` + scripts |
| Gray | Working artifact |

---

## 1. Development flow

```mermaid
---
config:
  layout: elk
---
flowchart TB
  subgraph RULES["Rules · docs/rules/"]
    direction TB
    AD[[agent-decisions]]
    RB[[rules-backend]]
    RF[[rules-frontend]]
    RT[[rules-testing]]
    RTH[[rules-theming]]
    RI18N[[rules-i18n]]
  end

  subgraph CONTEXT["Context · docs/context/"]
    direction TB
    CIDX[(INDEX · CODE-INDEX)]
    CBE[(api-list · be-services · fe-tests · be-tests)]
    CDS[(fe-design-system · fe-i18n)]
    CFE[(fe-components · fe-utils · fe-services)]
  end

  U([User goal]) --> PA[plan-agent]
  PA --> PM{{plan.md}}
  PM --> OR[orchestrator]
  OR --> NAV[navigator]
  NAV --> FIND{{findings.md}}

  NAV --> FDN[fe-design-navigator]
  NAV --> BAC[be-api-contract]

  FDN --> FD[fe-dev]
  FD --> FTH{{fe-test-handoff.md}}
  FTH --> FTA[fe-testing-agent]
  FTA --> FEV[flow-end-validator]

  BAC --> BD[be-dev]
  BD --> BTH{{be-test-handoff.md}}
  BTH --> BTA[be-testing-agent]
  BTA --> FEV

  PA -.-> AD
  PA -.-> CIDX
  NAV -.-> CIDX
  FDN -.-> CDS
  FDN -.-> RTH
  FDN -.-> RI18N
  BAC -.-> CBE
  BD -.-> CBE
  BD -.-> RB
  BTA -.-> RT
  BTA -.-> CBE
  BTA -.-> BTH
  FD -.-> CFE
  FD -.-> CDS
  FD -.-> RF
  FD -.-> RTH
  FD -.-> RI18N
  FTA -.-> RT
  FTA -.-> RI18N
  FTA -.-> CFE
  FTA -.-> FTH
  FEV -.-> CIDX

  classDef user fill:#fce7f3,stroke:#db2777,color:#831843
  classDef agent fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
  classDef rule fill:#fef3c7,stroke:#d97706,color:#92400e
  classDef context fill:#dcfce7,stroke:#16a34a,color:#14532d
  classDef artifact fill:#f1f5f9,stroke:#64748b,color:#334155

  class U user
  class PA,OR,NAV,FDN,BAC,BD,BTA,FD,FTA,FEV agent
  class AD,RT,RB,RF,RTH,RI18N rule
  class CIDX,CFE,CDS,CBE context
  class PM,FIND,BTH,FTH artifact
```

Orchestrator runs **one step per turn** from `plan.md`. Skip BE or FE branch when scope is API-only or UI-only.

---

## 2. Debugging flow

```mermaid
---
config:
  layout: elk
---
flowchart TB
  subgraph RULES["Rules · docs/rules/"]
    direction LR
    AD[[agent-decisions]]
    RT[[rules-testing]]
    TGT[[test-gap.template]]
  end

  subgraph CONTEXT["Context · docs/context/"]
    direction LR
    CIDX[(INDEX · CODE-INDEX)]
    CFE[(fe-tests · fe-components · fe-utils)]
    CBE[(be-tests · api-list · be-services)]
  end

  subgraph INDEX["Index · scripts + .code-index/"]
    direction LR
    GDB[(graph.db)]
    QRY[(who_uses · symbol_deps)]
    REF[(code_index_refresh.py)]
  end

  U([Bug report]) --> PA[plan-agent]
  PA --> PM{{plan.md}}
  PM --> OR[orchestrator]
  OR --> NAV[navigator]

  NAV --> BDBG[be-debugger]
  NAV --> FDBG[fe-debugger]

  BDBG --> TG{{test-gap.md}}
  FDBG --> TG

  TG --> BTA[be-testing-agent]
  TG --> FTA[fe-testing-agent]

  BTA --> FEV[flow-end-validator]
  FTA --> FEV

  PA -.-> AD
  PA -.-> CIDX
  NAV -.-> CIDX
  NAV -.-> GDB
  NAV -.-> QRY
  BDBG -.-> RT
  BDBG -.-> CBE
  BDBG -.-> GDB
  TG -.-> TGT
  FDBG -.-> RT
  FDBG -.-> CFE
  FDBG -.-> GDB
  BTA -.-> RT
  BTA -.-> TG
  BTA -.-> CBE
  FTA -.-> RT
  FTA -.-> TG
  FTA -.-> CFE
  FEV -.-> CIDX
  FEV -.-> REF
  REF -.-> GDB

  classDef user fill:#fce7f3,stroke:#db2777,color:#831843
  classDef agent fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
  classDef rule fill:#fef3c7,stroke:#d97706,color:#92400e
  classDef context fill:#dcfce7,stroke:#16a34a,color:#14532d
  classDef index fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
  classDef artifact fill:#f1f5f9,stroke:#64748b,color:#334155

  class U user
  class PA,OR,NAV,BDBG,FDBG,BTA,FTA,FEV agent
  class AD,RT,TGT rule
  class CIDX,CFE,CBE context
  class GDB,QRY,REF index
  class PM,TG artifact
```

One lane per task (**BE** or **FE**). Testing step is never skipped when `test-gap.md` exists.
