from utilities.debt_statistics_calculator import DebtStatisticsCalculator, DebtStatisticsForManyFiles, MetricStatistics, RiskLevelEnum
from services.file_metrics_service import FileMetrics

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

# il faut qu'une liste soit ordonnée pour calculer la médiane.
# 
#def test_get_medians():
#    # arrange
#    calculator = DebtStatisticsCalculator()
#    file_metrics = [
#        FileMetrics('file0', "file0.py", 32.4, 3, 50, 20),
#        FileMetrics('file1', "file1.py", 17.3, 11, 29, 15),
#        FileMetrics('file2', "file2.py", 49.2, 20, 80, 10),
#        FileMetrics('file3', "file3.py", 46.9, 31, 20, 25),
#    ]
#
#    # act
#    result = calculator.get_medians(file_metrics)
#
#    # arrange
#    assert result.avg_complexity == (17.3+49.2)/2.0
#    assert result.identifiable_entities == (11+20)/2.0
#    assert result.duplication_count == (29+80)/2.0
#    assert result.lines_duplicated == (17.3+49.2)/2.0

def test_get_priority():
    # arrange
    calculator = DebtStatisticsCalculator()

    # act
    result = calculator.get_priority(30.0/300.0,  50.0/200.0, 10.0/150.0, 3.0/400.0)

    # arrange
    assert result == 1.0 - (30.0/300.0 * 0.4 + 50.0/200.0 * 0.3 + 10.0/150.0 * 0.2 + 3.0/400.0 * 0.1)
    return

