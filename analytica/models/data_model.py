# ============================================
# ANALYSTIC.A — DATA MODELING ENGINE
# Relacionamentos entre tabelas + DAX simplificado
# ============================================
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# ============================================
# MODELOS DE DADOS
# ============================================

@dataclass
class Column:
    name: str
    dtype: str  # string, number, date, boolean
    is_key: bool = False
    is_foreign_key: bool = False
    references: Optional[str] = None  # "tabela.coluna"

@dataclass
class Table:
    name: str
    columns: List[Column]
    row_count: int = 0
    source: str = "upload"  # upload, database, api

@dataclass  
class Relationship:
    id: str
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    cardinality: str = "many-to-one"  # one-to-one, one-to-many, many-to-one, many-to-many
    cross_filter: str = "single"  # single, both

@dataclass
class Measure:
    name: str
    expression: str  # DAX simplificado
    format: str = "number"  # number, currency, percent, date
    description: str = ""

@dataclass
class DataModel:
    id: str
    name: str
    tables: List[Table]
    relationships: List[Relationship]
    measures: List[Measure]
    created_at: str
    updated_at: str
    owner: str


# ============================================
# STORAGE DE MODELOS
# ============================================
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "models")
os.makedirs(MODELS_DIR, exist_ok=True)


def save_model(model: DataModel) -> bool:
    """Salva modelo no disco"""
    try:
        filepath = os.path.join(MODELS_DIR, f"{model.id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            data = {
                "id": model.id,
                "name": model.name,
                "tables": [{"name": t.name, "columns": [asdict(c) for c in t.columns], "row_count": t.row_count, "source": t.source} for t in model.tables],
                "relationships": [asdict(r) for r in model.relationships],
                "measures": [asdict(m) for m in model.measures],
                "created_at": model.created_at,
                "updated_at": datetime.now().isoformat(),
                "owner": model.owner
            }
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving model: {e}")
        return False


def load_model(model_id: str) -> Optional[DataModel]:
    """Carrega modelo do disco"""
    try:
        filepath = os.path.join(MODELS_DIR, f"{model_id}.json")
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        tables = [
            Table(
                name=t["name"],
                columns=[Column(**c) for c in t["columns"]],
                row_count=t.get("row_count", 0),
                source=t.get("source", "upload")
            ) for t in data["tables"]
        ]
        
        relationships = [Relationship(**r) for r in data["relationships"]]
        measures = [Measure(**m) for m in data["measures"]]
        
        return DataModel(
            id=data["id"],
            name=data["name"],
            tables=tables,
            relationships=relationships,
            measures=measures,
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            owner=data["owner"]
        )
    except Exception as e:
        print(f"Error loading model: {e}")
        return None


def list_models(owner: str = None) -> List[Dict]:
    """Lista todos os modelos"""
    models = []
    for filename in os.listdir(MODELS_DIR):
        if filename.endswith('.json'):
            model = load_model(filename[:-5])
            if model:
                if owner is None or model.owner == owner:
                    models.append({
                        "id": model.id,
                        "name": model.name,
                        "tables_count": len(model.tables),
                        "updated_at": model.updated_at,
                        "owner": model.owner
                    })
    return models


def delete_model(model_id: str) -> bool:
    """Deleta um modelo"""
    try:
        filepath = os.path.join(MODELS_DIR, f"{model_id}.json")
        os.remove(filepath)
        return True
    except:
        return False


# ============================================
# DAX SIMPLIFICADO (PARSER)
# ============================================
DAX_FUNCTIONS = {
    "SUM": lambda col, data: sum(data.get(col, [])),
    "AVERAGE": lambda col, data: sum(data.get(col, [])) / len(data.get(col, [1])),
    "COUNT": lambda col, data: len(data.get(col, [])),
    "MIN": lambda col, data: min(data.get(col, [0])),
    "MAX": lambda col, data: max(data.get(col, [0])),
    "DISTINCTCOUNT": lambda col, data: len(set(data.get(col, []))),
}


def parse_dax(expression: str, data: Dict[str, List]) -> Any:
    """
    Parser DAX simplificado
    Suporta: SUM, AVERAGE, COUNT, MIN, MAX, DISTINCTCOUNT
    Exemplo: SUM(Vendas[Valor])
    """
    expression = expression.strip()
    
    for func_name, func in DAX_FUNCTIONS.items():
        if expression.upper().startswith(func_name + "("):
            # Extrai a coluna
            inner = expression[len(func_name)+1:-1]  # Remove FUNC( e )
            
            # Parse Tabela[Coluna]
            if "[" in inner and "]" in inner:
                table = inner.split("[")[0]
                column = inner.split("[")[1].rstrip("]")
                key = f"{table}.{column}"
            else:
                key = inner
            
            return func(key, data)
    
    # Operações matemáticas simples
    try:
        return eval(expression, {"__builtins__": {}}, data)
    except:
        return None


def validate_dax(expression: str) -> Dict:
    """Valida expressão DAX"""
    result = {"valid": True, "errors": [], "warnings": []}
    
    # Verifica funções conhecidas
    known_funcs = list(DAX_FUNCTIONS.keys())
    has_func = any(expression.upper().startswith(f + "(") for f in known_funcs)
    
    if not has_func and "[" not in expression:
        result["warnings"].append("Expressão não usa funções DAX padrão")
    
    # Verifica balanceamento de parênteses
    if expression.count("(") != expression.count(")"):
        result["valid"] = False
        result["errors"].append("Parênteses não balanceados")
    
    # Verifica balanceamento de colchetes
    if expression.count("[") != expression.count("]"):
        result["valid"] = False
        result["errors"].append("Colchetes não balanceados")
    
    return result


# ============================================
# FUNÇÕES DE RELACIONAMENTO
# ============================================

def create_relationship(
    model: DataModel,
    from_table: str,
    from_column: str,
    to_table: str,
    to_column: str,
    cardinality: str = "many-to-one"
) -> Relationship:
    """Cria relacionamento entre tabelas"""
    import uuid
    
    rel = Relationship(
        id=str(uuid.uuid4())[:8],
        from_table=from_table,
        from_column=from_column,
        to_table=to_table,
        to_column=to_column,
        cardinality=cardinality
    )
    
    model.relationships.append(rel)
    return rel


def detect_relationships(model: DataModel) -> List[Dict]:
    """Detecta automaticamente possíveis relacionamentos"""
    suggestions = []
    
    for table1 in model.tables:
        for table2 in model.tables:
            if table1.name == table2.name:
                continue
                
            for col1 in table1.columns:
                for col2 in table2.columns:
                    # Detecta por nome similar
                    if col1.name.lower() == col2.name.lower():
                        suggestions.append({
                            "from": f"{table1.name}.{col1.name}",
                            "to": f"{table2.name}.{col2.name}",
                            "confidence": 0.9,
                            "reason": "Nomes idênticos"
                        })
                    # Detecta padrão id/foreign_key
                    elif col1.name.lower() == f"{table2.name.lower()}_id":
                        suggestions.append({
                            "from": f"{table1.name}.{col1.name}",
                            "to": f"{table2.name}.id",
                            "confidence": 0.95,
                            "reason": "Padrão FK detectado"
                        })
    
    return suggestions


# ============================================
# FUNÇÕES DE MEDIDAS
# ============================================

def create_measure(
    model: DataModel,
    name: str,
    expression: str,
    format: str = "number",
    description: str = ""
) -> Optional[Measure]:
    """Cria nova medida"""
    validation = validate_dax(expression)
    
    if not validation["valid"]:
        return None
    
    measure = Measure(
        name=name,
        expression=expression,
        format=format,
        description=description
    )
    
    model.measures.append(measure)
    return measure


# ============================================
# QUICK MEASURES (Medidas Rápidas)
# ============================================

QUICK_MEASURES = {
    "total": lambda table, col: f"SUM({table}[{col}])",
    "media": lambda table, col: f"AVERAGE({table}[{col}])",
    "contagem": lambda table, col: f"COUNT({table}[{col}])",
    "contagem_distinta": lambda table, col: f"DISTINCTCOUNT({table}[{col}])",
    "minimo": lambda table, col: f"MIN({table}[{col}])",
    "maximo": lambda table, col: f"MAX({table}[{col}])",
    "variacao_percentual": lambda table, col: f"(SUM({table}[{col}]) - SUM({table}[{col}_anterior])) / SUM({table}[{col}_anterior])",
    "acumulado": lambda table, col: f"CALCULATE(SUM({table}[{col}]), FILTER(ALL({table}), {table}[Data] <= MAX({table}[Data])))",
}


def get_quick_measure(measure_type: str, table: str, column: str) -> Optional[str]:
    """Retorna expressão DAX para medida rápida"""
    if measure_type in QUICK_MEASURES:
        return QUICK_MEASURES[measure_type](table, column)
    return None
