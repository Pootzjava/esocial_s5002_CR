"""
Módulo de Inteligência Artificial para detecção de anomalias em dados do eSocial.
Implementa algoritmos para identificar inconsistências nos rendimentos declarados.
"""
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AnomalyResult:
    """Resultado da detecção de anomalia."""
    employee_id: str
    field: str
    expected_value: float
    actual_value: float
    deviation_percentage: float
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    timestamp: datetime


class AnomalyDetector:
    """Detector de anomalias baseado em estatística e regras de negócio."""
    
    def __init__(self, threshold_medium: float = 2.0, threshold_high: float = 3.0):
        self.threshold_medium = threshold_medium
        self.threshold_high = threshold_high
    
    def detect_salary_anomalies(
        self, 
        historical_salaries: List[float], 
        current_salary: float,
        employee_role: str = ""
    ) -> Optional[AnomalyResult]:
        """
        Detecta anomalias no salário atual comparado com histórico.
        
        Args:
            historical_salaries: Lista de salários históricos
            current_salary: Salário atual declarado
            employee_role: Cargo do funcionário (para regras específicas)
            
        Returns:
            AnomalyResult se anomalia detectada, None caso contrário
        """
        if len(historical_salaries) < 2:
            return None
        
        mean_salary = np.mean(historical_salaries)
        std_salary = np.std(historical_salaries)
        
        if std_salary == 0:
            std_salary = mean_salary * 0.1  # Evita divisão por zero
        
        z_score = abs(current_salary - mean_salary) / std_salary
        deviation_pct = ((current_salary - mean_salary) / mean_salary) * 100 if mean_salary > 0 else 0
        
        severity = self._classify_severity(z_score)
        
        if severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            return AnomalyResult(
                employee_id="EMP_001",  # Será preenchido pelo caller
                field="base_salary",
                expected_value=mean_salary,
                actual_value=current_salary,
                deviation_percentage=deviation_pct,
                severity=severity,
                description=f"Salário atual diverge {deviation_pct:.2f}% da média histórica",
                timestamp=datetime.now()
            )
        
        return None
    
    def detect_bonus_anomalies(
        self,
        historical_bonuses: List[float],
        current_bonus: float,
        industry_average: Optional[float] = None
    ) -> Optional[AnomalyResult]:
        """
        Detecta anomalias em bônus/gratificações.
        
        Args:
            historical_bonuses: Histórico de bônus do funcionário
            current_bonus: Bônus atual
            industry_average: Média da indústria para comparação
            
        Returns:
            AnomalyResult se anomalia detectada
        """
        if not historical_bonuses and not industry_average:
            return None
        
        reference_value = np.mean(historical_bonuses) if historical_bonuses else industry_average
        
        if reference_value == 0:
            reference_value = current_bonus * 0.5  # Fallback
        
        deviation_pct = abs((current_bonus - reference_value) / reference_value) * 100
        z_score = deviation_pct / 100  # Simplificação
        
        severity = self._classify_severity(z_score)
        
        if severity in ["HIGH", "CRITICAL"] or (deviation_pct > 200 and not historical_bonuses):
            return AnomalyResult(
                employee_id="EMP_001",
                field="bonus",
                expected_value=reference_value,
                actual_value=current_bonus,
                deviation_percentage=deviation_pct,
                severity=severity,
                description=f"Bônus atual diverge {deviation_pct:.2f}% do padrão esperado",
                timestamp=datetime.now()
            )
        
        return None
    
    def _classify_severity(self, z_score: float) -> str:
        """Classifica severidade baseada no z-score."""
        if z_score < self.threshold_medium:
            return "LOW"
        elif z_score < self.threshold_high:
            return "MEDIUM"
        elif z_score < 4.0:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def batch_detect(
        self, 
        employees_data: List[Dict[str, Any]]
    ) -> List[AnomalyResult]:
        """
        Executa detecção em lote para múltiplos funcionários.
        
        Args:
            employees_data: Lista de dicionários com dados dos funcionários
            
        Returns:
            Lista de AnomalyResult encontradas
        """
        results = []
        
        for emp in employees_data:
            # Detecção de salário
            salary_anomaly = self.detect_salary_anomalies(
                historical_salaries=emp.get("historical_salaries", []),
                current_salary=emp.get("current_salary", 0),
                employee_role=emp.get("role", "")
            )
            if salary_anomaly:
                salary_anomaly.employee_id = emp.get("employee_id", "UNKNOWN")
                results.append(salary_anomaly)
            
            # Detecção de bônus
            bonus_anomaly = self.detect_bonus_anomalies(
                historical_bonuses=emp.get("historical_bonuses", []),
                current_bonus=emp.get("current_bonus", 0),
                industry_average=emp.get("industry_avg_bonus")
            )
            if bonus_anomaly:
                bonus_anomaly.employee_id = emp.get("employee_id", "UNKNOWN")
                results.append(bonus_anomaly)
        
        return results
