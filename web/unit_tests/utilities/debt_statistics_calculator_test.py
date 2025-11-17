from src.utilities.debt_statistics_calculator import DebtStatisticsCalculator, DebtStatisticsForManyFiles, MetricStatistics, RiskLevelEnum
from src.services.file_metrics_service import FileMetrics
from src.utilities.custom_json_encoder import CustomJsonEncoder
import src.services.github_service as gs

def test_get_maximums():
    # arrange
    calculator = DebtStatisticsCalculator()
    file_metrics = [
        FileMetrics('file0', "file0.py", 32.4, 3, 50, 20),
        FileMetrics('file1', "file1.py", 17.3, 11, 29, 15),
        FileMetrics('file2', "file2.py", 49.2, 20, 80, 10),
        FileMetrics('file3', "file3.py", 46.9, 31, 20, 25),
    ]

    # act
    result = calculator.get_maximums(file_metrics)

    # assert
    assert result.avg_complexity == 49.2
    assert result.identifiable_entities == 31
    assert result.duplication_count == 80
    assert result.lines_duplicated == 25
    return

def test_get_averages(): 
    # arrange
    calculator = DebtStatisticsCalculator()
    file_metrics = [
        FileMetrics('file0', "file0.py", 32.4, 3, 50, 20),
        FileMetrics('file1', "file1.py", 17.3, 11, 29, 15),
        FileMetrics('file2', "file2.py", 49.2, 20, 80, 10),
        FileMetrics('file3', "file3.py", 46.9, 31, 20, 25),
    ]

    # act
    result = calculator.get_averages(file_metrics)

    # arrange
    assert result.avg_complexity == (32.4+17.3+49.2+46.9)/4.0
    assert result.identifiable_entities == (3+11+20+31)/4.0
    assert result.duplication_count == (50+29+80+20)/4.0
    assert result.lines_duplicated == (20+15+10+25)/4.0
    return
 
def test_get_medians__even():
    # arrange
    calculator = DebtStatisticsCalculator()
    file_metrics = [
        FileMetrics('file0', "file0.py", 32.4, 3, 50, 20),
        FileMetrics('file1', "file1.py", 17.3, 11, 29, 15),
        FileMetrics('file2', "file2.py", 49.2, 20, 80, 10),
        FileMetrics('file3', "file3.py", 46.9, 31, 20, 25),
    ]

    # act
    result = calculator.get_medians(file_metrics)

    # arrange
    assert result.avg_complexity == (32.4+46.9)/2.0
    assert result.identifiable_entities == (11+20)/2.0
    assert result.duplication_count == (29+50)/2.0
    assert result.lines_duplicated == (20+15)/2.0

def test_get_medians__odd():
    # arrange
    calculator = DebtStatisticsCalculator()
    file_metrics = [
        FileMetrics('file0', "file0.py", 32.4, 3, 50, 20),
        FileMetrics('file1', "file1.py", 17.3, 11, 29, 15),
        FileMetrics('file2', "file2.py", 49.2, 20, 80, 10),
        FileMetrics('file3', "file3.py", 46.9, 31, 20, 25),
        FileMetrics('file4', "file4.py", 11.3, 23, 30, 12),
    ]

    # act
    result = calculator.get_medians(file_metrics)

    # arrange
    assert result.avg_complexity == 32.4
    assert result.identifiable_entities == 20
    assert result.duplication_count == 30
    assert result.lines_duplicated == 15

def test_get_medians__one():
    # arrange
    calculator = DebtStatisticsCalculator()
    file_metrics = [
        FileMetrics('file0', "file0.py", 32.4, 3, 50, 20)
    ]

    # act
    result = calculator.get_medians(file_metrics)

    # arrange
    assert result.avg_complexity == 32.4
    assert result.identifiable_entities == 3
    assert result.duplication_count == 50
    assert result.lines_duplicated == 20

def test_get_medians__none():
    # arrange
    calculator = DebtStatisticsCalculator()
    file_metrics = []

    # act
    result = calculator.get_medians(file_metrics)

    # arrange
    assert result.avg_complexity == 0.0
    assert result.identifiable_entities == 0.0
    assert result.duplication_count == 0.0
    assert result.lines_duplicated == 0.0

def test_get_priority():
    # arrange
    calculator = DebtStatisticsCalculator()
    f = FileMetrics('file0', "file0.py", 32.4, 3.0, 50.0, 20.0)
    maximums = MetricStatistics(49.2, 31.0, 80.0, 25.0)

    # act
    result = calculator.get_priority(f, maximums)

    # arrange
    assert result == ((32.4/49.2)*0.40+(3.0/31.0)*0.30+(50.0/80.0)*0.20+(20.0/25.0)*0.10)
    return

def test_get_risk_level(): 
    # arrange
    calculator = DebtStatisticsCalculator()

    # act
    result0 = calculator.get_risk_level(1)
    result1 = calculator.get_risk_level(11)
    result2 = calculator.get_risk_level(21)
    result3 = calculator.get_risk_level(31)
    result4 = calculator.get_risk_level(41)
    result5 = calculator.get_risk_level(51)

    # assert
    assert result0 == RiskLevelEnum.LOW_RISK
    assert result1 == RiskLevelEnum.MEDIUM_RISK
    assert result2 == RiskLevelEnum.HIGH_RISK
    assert result3 == RiskLevelEnum.HIGH_RISK
    assert result4 == RiskLevelEnum.HIGH_RISK
    assert result5 == RiskLevelEnum.VERY_HIGH_RISK
    return

def test_get_ratio():
    # arrange 
    calculator = DebtStatisticsCalculator()

    # act
    result0 = calculator.get_ratio(10, 5)
    result1 = calculator.get_ratio(0, 3)

    # assert
    assert result0 == 0.5
    assert result1 == 0.0
    return
    
def test_get_debt_statistics_for_many_files():
    # arrange
    calculator = DebtStatisticsCalculator()
    file_metrics = [
        FileMetrics('file0', "file0.py", 32.4, 3, 50, 20),
        FileMetrics('file1', "file1.py", 17.3, 11, 29, 15),
        FileMetrics('file2', "file2.py", 49.2, 20, 80, 10),
        FileMetrics('file3', "file3.py", 46.9, 31, 20, 25),
    ]

    # act
    result = calculator.get_debt_statistics_for_many_files(file_metrics)

    # assert
    assert result.priorities[0][1] == ((49.2/49.2)*0.40+(20.0/31.0)*0.30+(80.0/80.0)*0.20+(10.0/25.0)*0.10)
    assert result.priorities[0][0] == 'file2.py'
    assert result.risks[0][1] == RiskLevelEnum.HIGH_RISK 
    assert result.risks[0][0] == 'file0.py'

    print(gs.repo_cache_root())
    print(gs.repo_dir("Flip-HH", "pfe021-test-repo"))
    assert False
