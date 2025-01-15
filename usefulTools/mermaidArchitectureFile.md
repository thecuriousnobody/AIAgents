graph TD
    subgraph Client Layer ["Client Layer (Vercel)"]
        A[Landing Page] --> B[React + Tailwind UI]
        B --> C[User Authentication]
        B --> D[WebSocket Connection]
    end

    subgraph Authentication ["Authentication & Storage (Firebase)"]
        C --> E[Firebase Auth]
        E --> F[Firestore DB]
        F --> G[User Profiles]
        F --> H[API Keys]
    end

    subgraph Backend Services ["Backend Services (Firebase Functions)"]
        I[FastAPI Server] --> J[WebSocket Manager]
        J --> K[Real-time Updates]
        I --> L[Agent Orchestrator]
    end

    subgraph Agent Layer ["AI Agent Layer"]
        L --> M[Podcast Guest Finder]
        L --> N[Email Creator]
        L --> O[Script Generator]
        L --> P[Blog Creator]
        
        subgraph Agent Components
            M --> Q[Topic Analyzer]
            M --> R[Expert Finder]
            M --> S[Contact Researcher]
        end
    end

    subgraph External Services ["External Services"]
        T[Claude API]
        U[Google Search API]
        V[DuckDuckGo API]
    end

    %% Data Flow Connections
    D --> J
    L --> T
    M --> U
    M --> V
    K --> B

    style Client Layer fill:#ff6b4a,stroke:#333,stroke-width:2px
    style Authentication fill:#4a90e2,stroke:#333,stroke-width:2px
    style Backend Services fill:#50c878,stroke:#333,stroke-width:2px
    style Agent Layer fill:#ffd700,stroke:#333,stroke-width:2px
    style External Services fill:#c0c0c0,stroke:#333,stroke-width:2px