import os
import subprocess

diagrams = {
    "register_activity": """flowchart TD
    subgraph Developer
        direction TB
        Start(( )) --> A[Enter details]
        A --> B[Click Register]
    end
    subgraph System
        direction TB
        C{Is input valid?}
        D[Hash Password & Save to IAM DB]
        E[Generate JWT Tokens]
        F[Show Error Message]
    end
    B --> C
    C -- Yes --> D
    D --> E
    C -- No --> F
    E --> End((( )))
    F --> End
""",

    "login_activity": """flowchart TD
    subgraph Developer
        direction TB
        Start(( )) --> A[Enter credentials]
        A --> B[Click Login]
    end
    subgraph System
        direction TB
        C{Is valid?}
        D[Verify Hash & Fetch User]
        E[Generate JWT & Save to Redis]
        F[Show Error Message]
    end
    B --> C
    C -- Yes --> D
    D --> E
    C -- No --> F
    E --> End((( )))
    F --> End
""",

    "login_with_gmail_activity": """flowchart TD
    subgraph Developer
        direction TB
        Start(( )) --> A[Click Login with Google]
        A --> B[Authorize in Google Modal]
    end
    subgraph System
        direction TB
        C{Is Authorized?}
        D[Exchange Auth Code]
        E[Find or Create User in IAM]
        F[Generate JWT & Save to Redis]
        G[Show Error Message]
    end
    B --> C
    C -- Yes --> D
    D --> E
    E --> F
    C -- No --> G
    F --> End((( )))
    G --> End
""",

    "update_profile_activity": """flowchart TD
    subgraph Developer
        direction TB
        Start(( )) --> A[Edit profile details]
        A --> B[Click Save]
    end
    subgraph System
        direction TB
        C{Is valid?}
        D[Update User in MetaDB]
        E[Show Error Message]
    end
    B --> C
    C -- Yes --> D
    C -- No --> E
    D --> End((( )))
    E --> End
""",

    "create_project_activity": """flowchart TD
    subgraph Developer
        direction TB
        Start(( )) --> A[Enter project info]
        A --> B[Click Create]
    end
    subgraph System
        direction TB
        C{Is valid?}
        D[Save to MetaDB status:creating]
        E[Inject K8s Secret]
        F[Apply CRD to K3s]
        G[Show Error Message]
    end
    B --> C
    C -- Yes --> D
    D --> E
    E --> F
    C -- No --> G
    F --> End((( )))
    G --> End
""",

    "create_schema_activity": """flowchart TD
    subgraph Developer
        direction TB
        Start(( )) --> A[Define Schema in Visual Builder]
        A --> B[Click Save/Execute]
    end
    subgraph System
        direction TB
        C{Is valid?}
        D[Generate Raw DDL CREATE TABLE]
        E[Retrieve Credentials via DSNService]
        F[Execute DDL on Tenant DB]
        G[Show Error Message]
    end
    B --> C
    C -- Yes --> D
    D --> E
    E --> F
    C -- No --> G
    F --> End((( )))
    G --> End
""",

    "delete_project_activity": """flowchart TD
    subgraph Developer
        direction TB
        Start(( )) --> A[Click Delete Project]
        A --> B[Confirm Deletion]
    end
    subgraph System
        direction TB
        C{Is confirmed?}
        D[Delete K8s CRD]
        E[Evict Connection Pools]
        F[Remove from MetaDB]
        G[Cancel Operation]
    end
    B --> C
    C -- Yes --> D
    D --> E
    E --> F
    C -- No --> G
    F --> End((( )))
    G --> End
""",

    "delete_rows_activity": """flowchart TD
    subgraph Developer
        direction TB
        Start(( )) --> A[Select Rows]
        A --> B[Click Delete]
    end
    subgraph System
        direction TB
        C{Is confirmed?}
        D[Forward DELETE to PostgREST]
        E[Execute on Tenant DB]
        F[Cancel Operation]
    end
    B --> C
    C -- Yes --> D
    D --> E
    C -- No --> F
    E --> End((( )))
    F --> End
""",

    "execute_query_activity": """flowchart TD
    subgraph Developer
        direction TB
        Start(( )) --> A[Enter SQL Query]
        A --> B[Click Run]
    end
    subgraph System
        direction TB
        C{Syntax OK?}
        D[Retrieve Credentials via DSNService]
        E[Execute Query via PGProxy]
        F[Return JSON Results]
        G[Show Syntax Error]
    end
    B --> C
    C -- Yes --> D
    D --> E
    E --> F
    C -- No --> G
    F --> End((( )))
    G --> End
""",

    "create_edit_table_activity": """flowchart TD
    subgraph Developer
        direction TB
        Start(( )) --> A[Modify Table Structure]
        A --> B[Click Save]
    end
    subgraph System
        direction TB
        C{Is valid?}
        D[Generate ALTER/CREATE DDL]
        E[Execute via DSNService]
        F[Show Error Message]
    end
    B --> C
    C -- Yes --> D
    D --> E
    C -- No --> F
    E --> End((( )))
    F --> End
""",

    "delete_table_activity": """flowchart TD
    subgraph Developer
        direction TB
        Start(( )) --> A[Click Drop Table]
        A --> B[Confirm]
    end
    subgraph System
        direction TB
        C{Is confirmed?}
        D[Generate DROP TABLE DDL]
        E[Execute via DSNService]
        F[Cancel Operation]
    end
    B --> C
    C -- Yes --> D
    D --> E
    C -- No --> F
    E --> End((( )))
    F --> End
""",

    "modify_entity_nosql_activity": """flowchart TD
    subgraph Developer
        direction TB
        Start(( )) --> A[Edit JSON Document]
        A --> B[Click Save]
    end
    subgraph System
        direction TB
        C{Is valid JSON?}
        D[Execute updateOne on MongoDB]
        E[Return Success]
        F[Show Error Message]
    end
    B --> C
    C -- Yes --> D
    D --> E
    C -- No --> F
    E --> End((( )))
    F --> End
""",

    "insert_update_row_activity": """flowchart TD
    subgraph Developer
        direction TB
        Start(( )) --> A[Enter Row Data]
        A --> B[Click Save]
    end
    subgraph System
        direction TB
        C{Is valid?}
        D[Forward POST/PATCH to PostgREST]
        E[Execute on Tenant DB]
        F[Show Error Message]
    end
    B --> C
    C -- Yes --> D
    D --> E
    C -- No --> F
    E --> End((( )))
    F --> End
""",

    "restore_project_activity": """flowchart TD
    subgraph Developer
        direction TB
        Start(( )) --> A[Select Backup Point]
        A --> B[Click Restore]
    end
    subgraph System
        direction TB
        C{Is valid?}
        D[Retrieve Backup Object]
        E[Stream to Tenant DB]
        F[Update MetaDB State]
        G[Show Error Message]
    end
    B --> C
    C -- Yes --> D
    D --> E
    E --> F
    C -- No --> G
    F --> End((( )))
    G --> End
""",

    "upgrade_tier_activity": """flowchart TD
    subgraph Developer
        direction TB
        Start(( )) --> A[Select New Tier]
        A --> B[Submit Payment]
    end
    subgraph System
        direction TB
        C{Payment Success?}
        D[Update MetaDB Tier]
        E[Patch K8s ResourceQuotas]
        F[Show Payment Error]
    end
    B --> C
    C -- Yes --> D
    D --> E
    C -- No --> F
    E --> End((( )))
    F --> End
""",

    "reset_password_activity": """flowchart TD
    subgraph Developer
        direction TB
        Start(( )) --> A[Request Reset Link]
        A --> B[Click Link & Enter New Password]
    end
    subgraph System
        direction TB
        C{Is valid?}
        D[Hash New Password]
        E[Update MetaDB]
        F[Show Error Message]
    end
    B --> C
    C -- Yes --> D
    D --> E
    C -- No --> F
    E --> End((( )))
    F --> End
""",

    "delete_account_activity": """flowchart TD
    subgraph Developer
        direction TB
        Start(( )) --> A[Click Delete Account]
        A --> B[Confirm Password]
    end
    subgraph System
        direction TB
        C{Is correct?}
        D[Cascade Delete K8s CRDs]
        E[Delete User from IAM MetaDB]
        F[Invalidate Redis Tokens]
        G[Show Error Message]
    end
    B --> C
    C -- Yes --> D
    D --> E
    E --> F
    C -- No --> G
    F --> End((( )))
    G --> End
"""
}

os.makedirs("/media/D/Eduaction/CS/GP/book/images/activity_mermaid", exist_ok=True)

# Use basic styling for flowchart to make it look clean like typical activity diagrams
mermaid_config = """%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#fffacd', 'primaryBorderColor': '#000', 'lineColor': '#000', 'textColor': '#000', 'fontFamily': 'arial' }}}%%
"""

for name, content in diagrams.items():
    filepath = f"/media/D/Eduaction/CS/GP/book/images/activity_mermaid/{name}.mmd"
    with open(filepath, "w") as f:
        f.write(mermaid_config + content)
    
    pdf_path = f"/media/D/Eduaction/CS/GP/book/images/activity_mermaid/{name}.pdf"
    print(f"Generating {pdf_path}")
    subprocess.run(["mmdc", "-i", filepath, "-o", pdf_path, "-b", "white", "-s", "2"], check=True)

print("Done generating all updated flowchart activity diagrams!")
