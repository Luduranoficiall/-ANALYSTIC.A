# ============================================
# ANALYSTIC.A — WORKSPACES & MULTI-USUÁRIO
# Áreas de trabalho compartilhadas + Permissões
# ============================================
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field

# ============================================
# DIRETÓRIOS
# ============================================
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
WORKSPACES_DIR = os.path.join(DATA_DIR, "workspaces")
USERS_DIR = os.path.join(DATA_DIR, "users")

os.makedirs(WORKSPACES_DIR, exist_ok=True)
os.makedirs(USERS_DIR, exist_ok=True)


# ============================================
# MODELOS
# ============================================

@dataclass
class Permission:
    user_id: str
    role: str  # owner, admin, editor, viewer
    granted_at: str = field(default_factory=lambda: datetime.now().isoformat())
    granted_by: str = ""


@dataclass
class Dashboard:
    id: str
    name: str
    description: str = ""
    is_public: bool = False
    public_url: str = ""
    embed_code: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    layout: Dict = field(default_factory=dict)  # Configuração dos tiles


@dataclass
class Workspace:
    id: str
    name: str
    description: str = ""
    owner: str = ""
    permissions: List[Permission] = field(default_factory=list)
    dashboards: List[Dashboard] = field(default_factory=list)
    datasets: List[str] = field(default_factory=list)  # IDs dos datasets
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    settings: Dict = field(default_factory=dict)


@dataclass
class UserProfile:
    id: str
    email: str
    name: str
    avatar: str = ""
    role: str = "user"  # admin, user, viewer
    workspaces: List[str] = field(default_factory=list)  # IDs dos workspaces
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    preferences: Dict = field(default_factory=dict)


# ============================================
# CRUD DE WORKSPACES
# ============================================

def create_workspace(name: str, owner: str, description: str = "") -> Workspace:
    """Cria novo workspace"""
    workspace = Workspace(
        id=str(uuid.uuid4())[:8],
        name=name,
        description=description,
        owner=owner,
        permissions=[Permission(user_id=owner, role="owner")],
        dashboards=[],
        datasets=[]
    )
    save_workspace(workspace)
    return workspace


def save_workspace(workspace: Workspace) -> bool:
    """Salva workspace no disco"""
    try:
        filepath = os.path.join(WORKSPACES_DIR, f"{workspace.id}.json")
        data = {
            "id": workspace.id,
            "name": workspace.name,
            "description": workspace.description,
            "owner": workspace.owner,
            "permissions": [asdict(p) for p in workspace.permissions],
            "dashboards": [asdict(d) for d in workspace.dashboards],
            "datasets": workspace.datasets,
            "created_at": workspace.created_at,
            "updated_at": datetime.now().isoformat(),
            "settings": workspace.settings
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving workspace: {e}")
        return False


def load_workspace(workspace_id: str) -> Optional[Workspace]:
    """Carrega workspace do disco"""
    try:
        filepath = os.path.join(WORKSPACES_DIR, f"{workspace_id}.json")
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return Workspace(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            owner=data["owner"],
            permissions=[Permission(**p) for p in data.get("permissions", [])],
            dashboards=[Dashboard(**d) for d in data.get("dashboards", [])],
            datasets=data.get("datasets", []),
            created_at=data["created_at"],
            updated_at=data.get("updated_at", ""),
            settings=data.get("settings", {})
        )
    except Exception as e:
        print(f"Error loading workspace: {e}")
        return None


def list_workspaces(user_id: str = None) -> List[Dict]:
    """Lista workspaces (filtrado por usuário se especificado)"""
    workspaces = []
    
    for filename in os.listdir(WORKSPACES_DIR):
        if filename.endswith('.json'):
            ws = load_workspace(filename[:-5])
            if ws:
                # Verifica se usuário tem acesso
                has_access = user_id is None or ws.owner == user_id
                if not has_access:
                    for perm in ws.permissions:
                        if perm.user_id == user_id:
                            has_access = True
                            break
                
                if has_access:
                    workspaces.append({
                        "id": ws.id,
                        "name": ws.name,
                        "description": ws.description,
                        "owner": ws.owner,
                        "dashboards_count": len(ws.dashboards),
                        "updated_at": ws.updated_at
                    })
    
    return workspaces


def delete_workspace(workspace_id: str, user_id: str) -> Dict:
    """Deleta workspace (apenas owner pode deletar)"""
    ws = load_workspace(workspace_id)
    if not ws:
        return {"success": False, "error": "Workspace não encontrado"}
    
    if ws.owner != user_id:
        return {"success": False, "error": "Apenas o proprietário pode deletar"}
    
    try:
        filepath = os.path.join(WORKSPACES_DIR, f"{workspace_id}.json")
        os.remove(filepath)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================
# PERMISSÕES
# ============================================

ROLE_PERMISSIONS = {
    "owner": ["read", "write", "delete", "share", "manage"],
    "admin": ["read", "write", "delete", "share"],
    "editor": ["read", "write"],
    "viewer": ["read"]
}


def add_user_to_workspace(
    workspace_id: str, 
    user_id: str, 
    role: str, 
    granted_by: str
) -> Dict:
    """Adiciona usuário ao workspace"""
    ws = load_workspace(workspace_id)
    if not ws:
        return {"success": False, "error": "Workspace não encontrado"}
    
    # Verifica se quem está adicionando tem permissão
    has_permission = False
    for perm in ws.permissions:
        if perm.user_id == granted_by and perm.role in ["owner", "admin"]:
            has_permission = True
            break
    
    if not has_permission:
        return {"success": False, "error": "Sem permissão para adicionar usuários"}
    
    # Verifica se usuário já existe
    for perm in ws.permissions:
        if perm.user_id == user_id:
            return {"success": False, "error": "Usuário já está no workspace"}
    
    # Adiciona permissão
    ws.permissions.append(Permission(
        user_id=user_id,
        role=role,
        granted_by=granted_by
    ))
    
    save_workspace(ws)
    return {"success": True}


def remove_user_from_workspace(
    workspace_id: str,
    user_id: str,
    removed_by: str
) -> Dict:
    """Remove usuário do workspace"""
    ws = load_workspace(workspace_id)
    if not ws:
        return {"success": False, "error": "Workspace não encontrado"}
    
    # Owner não pode ser removido
    if user_id == ws.owner:
        return {"success": False, "error": "Não é possível remover o proprietário"}
    
    # Verifica permissão de quem está removendo
    has_permission = False
    for perm in ws.permissions:
        if perm.user_id == removed_by and perm.role in ["owner", "admin"]:
            has_permission = True
            break
    
    if not has_permission:
        return {"success": False, "error": "Sem permissão para remover usuários"}
    
    # Remove
    ws.permissions = [p for p in ws.permissions if p.user_id != user_id]
    save_workspace(ws)
    
    return {"success": True}


def check_permission(workspace_id: str, user_id: str, action: str) -> bool:
    """Verifica se usuário tem permissão para ação"""
    ws = load_workspace(workspace_id)
    if not ws:
        return False
    
    for perm in ws.permissions:
        if perm.user_id == user_id:
            allowed_actions = ROLE_PERMISSIONS.get(perm.role, [])
            return action in allowed_actions
    
    return False


def get_user_role(workspace_id: str, user_id: str) -> Optional[str]:
    """Retorna role do usuário no workspace"""
    ws = load_workspace(workspace_id)
    if not ws:
        return None
    
    for perm in ws.permissions:
        if perm.user_id == user_id:
            return perm.role
    
    return None


# ============================================
# DASHBOARDS
# ============================================

def create_dashboard(
    workspace_id: str,
    name: str,
    user_id: str,
    description: str = ""
) -> Dict:
    """Cria dashboard no workspace"""
    if not check_permission(workspace_id, user_id, "write"):
        return {"success": False, "error": "Sem permissão"}
    
    ws = load_workspace(workspace_id)
    if not ws:
        return {"success": False, "error": "Workspace não encontrado"}
    
    dashboard = Dashboard(
        id=str(uuid.uuid4())[:8],
        name=name,
        description=description
    )
    
    ws.dashboards.append(dashboard)
    save_workspace(ws)
    
    return {"success": True, "dashboard": asdict(dashboard)}


def publish_dashboard(
    workspace_id: str,
    dashboard_id: str,
    user_id: str,
    is_public: bool = True
) -> Dict:
    """Publica dashboard (gera link público)"""
    if not check_permission(workspace_id, user_id, "share"):
        return {"success": False, "error": "Sem permissão para publicar"}
    
    ws = load_workspace(workspace_id)
    if not ws:
        return {"success": False, "error": "Workspace não encontrado"}
    
    for dashboard in ws.dashboards:
        if dashboard.id == dashboard_id:
            dashboard.is_public = is_public
            
            if is_public:
                # Gera URL pública
                public_token = str(uuid.uuid4())[:12]
                dashboard.public_url = f"/public/dashboard/{public_token}"
                dashboard.embed_code = f'<iframe src="https://analystica.app{dashboard.public_url}" width="100%" height="600" frameborder="0"></iframe>'
            else:
                dashboard.public_url = ""
                dashboard.embed_code = ""
            
            dashboard.updated_at = datetime.now().isoformat()
            save_workspace(ws)
            
            return {
                "success": True,
                "public_url": dashboard.public_url,
                "embed_code": dashboard.embed_code
            }
    
    return {"success": False, "error": "Dashboard não encontrado"}


def get_public_dashboard(public_token: str) -> Optional[Dict]:
    """Recupera dashboard público pelo token"""
    for filename in os.listdir(WORKSPACES_DIR):
        if filename.endswith('.json'):
            ws = load_workspace(filename[:-5])
            if ws:
                for dashboard in ws.dashboards:
                    if dashboard.public_url and public_token in dashboard.public_url:
                        if dashboard.is_public:
                            return {
                                "id": dashboard.id,
                                "name": dashboard.name,
                                "description": dashboard.description,
                                "layout": dashboard.layout,
                                "workspace_name": ws.name
                            }
    return None


# ============================================
# CRUD DE USUÁRIOS
# ============================================

def create_user_profile(email: str, name: str) -> UserProfile:
    """Cria perfil de usuário"""
    user = UserProfile(
        id=str(uuid.uuid4())[:8],
        email=email,
        name=name
    )
    save_user_profile(user)
    return user


def save_user_profile(user: UserProfile) -> bool:
    """Salva perfil do usuário"""
    try:
        filepath = os.path.join(USERS_DIR, f"{user.id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(user), f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving user: {e}")
        return False


def get_user_by_email(email: str) -> Optional[UserProfile]:
    """Busca usuário por email"""
    for filename in os.listdir(USERS_DIR):
        if filename.endswith('.json'):
            try:
                filepath = os.path.join(USERS_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if data.get("email") == email:
                    return UserProfile(**data)
            except:
                continue
    return None


# ============================================
# INICIALIZAÇÃO: WORKSPACE PADRÃO
# ============================================

def init_default_workspace():
    """Cria workspace padrão se não existir"""
    workspaces = list_workspaces()
    if not workspaces:
        ws = create_workspace(
            name="Meu Workspace",
            owner="admin",
            description="Workspace padrão do ANALYSTIC.A"
        )
        
        # Cria dashboard de exemplo
        create_dashboard(
            workspace_id=ws.id,
            name="Dashboard Principal",
            user_id="admin",
            description="Dashboard de exemplo"
        )
        
        return ws
    return None


# Inicializa ao importar
init_default_workspace()
