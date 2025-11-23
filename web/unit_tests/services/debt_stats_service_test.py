from src.services.debt_stats_service import DebtStatsService
from src.interface.tech_debt_report import TechDebtMetrics, TechDebtReport, RiskEnum

def test_get_statistics__maximum():
    # arrange
    file_list = {
        "file0.py": TechDebtMetrics(32.4, 3, 50, 20),
        "file1.py": TechDebtMetrics(17.3, 11, 29, 15),
        "file2.py": TechDebtMetrics(49.2, 20, 80, 10),
        "file3.py": TechDebtMetrics(46.9, 31, 20, 25),
    }
    which_stat = DebtStatsService.StatsEnum.MAXIMUMS
    service = DebtStatsService()

    # act
    maximums = service.get_statistics(which_stat, file_list)

    # assert
    assert maximums.average_complexity == 49.2
    assert maximums.entities == 31
    assert maximums.duplications == 80
    assert maximums.duplicated_lines == 25

def test_get_statistics__averages():
    # arrange
    file_list = {
        "file0.py": TechDebtMetrics(32.4, 3, 50, 20),
        "file1.py": TechDebtMetrics(17.3, 11, 29, 15),
        "file2.py": TechDebtMetrics(49.2, 20, 80, 10),
        "file3.py": TechDebtMetrics(46.9, 31, 20, 25),
    }
    which_stat = DebtStatsService.StatsEnum.AVERAGES
    service = DebtStatsService()

    # act
    averages = service.get_statistics(which_stat, file_list)

    # assert
    assert averages.average_complexity == (32.4+17.3+49.2+46.9)/4.0
    assert averages.entities == (3.0+11.0+20.0+31.0)/4.0
    assert averages.duplications == (50.0+29.0+80.0+20.0)/4.0
    assert averages.duplicated_lines == (20.0+15.0+10.0+25.0)/4.0

def test_get_statistics__medians():
    # arrange
    file_list = {
        "file0.py": TechDebtMetrics(32.4, 3, 50, 20),
        "file1.py": TechDebtMetrics(17.3, 11, 29, 15),
        "file2.py": TechDebtMetrics(49.2, 20, 80, 10),
        "file3.py": TechDebtMetrics(46.9, 31, 20, 25),
    }
    which_stat = DebtStatsService.StatsEnum.MEDIANS
    service = DebtStatsService()

    # act
    medians = service.get_statistics(which_stat, file_list)

    # assert
    assert medians.average_complexity == (32.4+46.9)/2.0
    assert medians.entities == (11.0+20.0)/2.0
    assert medians.duplications == (50.0+29.0)/2.0
    assert medians.duplicated_lines == (20.0+15.0)/2.0

def test_get_priority():
    # arrange
    ratios = TechDebtMetrics(32.4/49.2, 3.0/31.0, 50.0/80.0, 20.0/25.0)
    service = DebtStatsService()

    # act
    score = service.get_priority(ratios)

    # assert
    assert score == (32.4/49.2)*0.40 + (3.0/31.0)*0.30 + (50.0/80.0)*0.20 + (20.0/25.0)*0.10

def test_get_ratios():
    # arrange
    metrics = TechDebtMetrics(32.4, 3, 50, 20)
    maximums = TechDebtMetrics(49.2, 31, 80, 25)
    service = DebtStatsService()

    # act
    ratios = service.get_ratios(metrics, maximums)

    # assert 
    assert ratios.average_complexity == 32.4/49.2
    assert ratios.entities == 3.0/31.0
    assert ratios.duplications == 50.0/80.0
    assert ratios.duplicated_lines == 20.0/25.0

def test_get_ratios__maximum_zero():
    # arrange
    metrics = TechDebtMetrics(32.4, 3, 50, 20)
    maximums = TechDebtMetrics()
    service = DebtStatsService()

    # act
    ratios = service.get_ratios(metrics, maximums)

    # assert 
    assert ratios.average_complexity == 0.0
    assert ratios.entities == 0.0
    assert ratios.duplications == 0.0
    assert ratios.duplicated_lines == 0.0

def test_get_risk():
    # arrange
    service = DebtStatsService()

    # act
    risk0 = service.get_risk(1)
    risk1 = service.get_risk(11)
    risk2 = service.get_risk(21)
    risk3 = service.get_risk(51)

    # assert
    assert risk0 == RiskEnum.LOW_RISK
    assert risk1 == RiskEnum.MEDIUM_RISK
    assert risk2 == RiskEnum.HIGH_RISK
    assert risk3 == RiskEnum.VERY_HIGH_RISK

def test_get_report():
    # arrange
    class LocalServiceMock(DebtStatsService):
        stats_called = 0
        priority_called = 0
        risk_called = 0
        ratio_called = 0

        dummy = TechDebtMetrics(0.5, 0.5, 0.5, 0.5)
        
        def get_statistics(self, which_stat, file_list):
            LocalServiceMock.stats_called += 1
            return LocalServiceMock.dummy
        
        def get_ratios(self, metrics, maximums):
            LocalServiceMock.ratio_called += 1
            return LocalServiceMock.dummy
        
        def get_priority(self, ratios):
            LocalServiceMock.priority_called += 1
            return 0.5
        
        def get_risk(self, complexity):
            LocalServiceMock.risk_called += 1
            return RiskEnum.MEDIUM_RISK

    file_list = {
        "file0.py": TechDebtMetrics(32.4, 3, 50, 20),
        "file1.py": TechDebtMetrics(17.3, 11, 29, 15),
        "file2.py": TechDebtMetrics(49.2, 20, 80, 10),
        "file3.py": TechDebtMetrics(46.9, 31, 20, 25),
    }

    service = LocalServiceMock()

    # act
    report = service.get_debt_report(file_list)

    # assert
    assert LocalServiceMock.stats_called == 3
    assert LocalServiceMock.ratio_called == 4
    assert LocalServiceMock.priority_called == 4
    assert LocalServiceMock.risk_called == 4
    assert report.get_averages() == LocalServiceMock.dummy
    assert report.get_maximums() == LocalServiceMock.dummy
    assert report.get_medians() == LocalServiceMock.dummy
    assert report.get_length() == 4
    for report_element in report:
        assert report_element.priority == 0.5 and report_element.risk == RiskEnum.MEDIUM_RISK
