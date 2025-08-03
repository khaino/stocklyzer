"""Tests for domain models."""

import pytest
from decimal import Decimal
from datetime import datetime
from stocklyzer.domain.models import StockInfo, GrowthMetrics, PriceRange


class TestStockInfoDividend:
    """Test dividend functionality in StockInfo model."""

    def test_stock_with_dividend(self):
        """Test stock with dividend information."""
        stock = StockInfo(
            symbol="AAPL",
            company_name="Apple Inc.",
            current_price=Decimal("200.00"),
            change=Decimal("1.00"),
            change_percent=Decimal("0.50"),
            open_price=Decimal("199.00"),
            high_price=Decimal("201.00"),
            low_price=Decimal("198.00"),
            volume=1000000,
            last_updated=datetime.now(),
            dividend_yield=Decimal("0.51"),
            dividend_rate=Decimal("1.04")
        )
        
        assert stock.pays_dividend is True
        assert stock.dividend_yield == Decimal("0.51")
        assert stock.dividend_rate == Decimal("1.04")

    def test_stock_without_dividend(self):
        """Test stock without dividend information."""
        stock = StockInfo(
            symbol="TSLA",
            company_name="Tesla Inc.",
            current_price=Decimal("300.00"),
            change=Decimal("-5.00"),
            change_percent=Decimal("-1.67"),
            open_price=Decimal("305.00"),
            high_price=Decimal("306.00"),
            low_price=Decimal("299.00"),
            volume=2000000,
            last_updated=datetime.now(),
            dividend_yield=None,
            dividend_rate=None
        )
        
        assert stock.pays_dividend is False
        assert stock.dividend_yield is None
        assert stock.dividend_rate is None

    def test_dividend_yield_validation(self):
        """Test that dividend yield is properly quantized."""
        stock = StockInfo(
            symbol="KO",
            company_name="Coca-Cola Company",
            current_price=Decimal("70.00"),
            change=Decimal("0.50"),
            change_percent=Decimal("0.72"),
            open_price=Decimal("69.50"),
            high_price=Decimal("70.50"),
            low_price=Decimal("69.00"),
            volume=1500000,
            last_updated=datetime.now(),
            dividend_yield=Decimal("2.965"),
            dividend_rate=Decimal("2.04")
        )
        
        # Should be quantized to 2 decimal places
        assert stock.dividend_yield == Decimal("2.96")
        assert stock.dividend_rate == Decimal("2.04")
        assert stock.pays_dividend is True

    def test_growth_metrics_with_three_years(self):
        """Test that GrowthMetrics includes 3-year growth."""
        from stocklyzer.domain.models import GrowthMetrics
        
        growth = GrowthMetrics(
            one_year=Decimal("-7.52"),
            two_years=Decimal("6.14"),
            three_years=Decimal("25.48"),
            five_years=Decimal("91.11"),
            ten_years=Decimal("662.93")
        )
        
        assert growth.one_year == Decimal("-7.52")
        assert growth.two_years == Decimal("6.14")
        assert growth.three_years == Decimal("25.48")
        assert growth.five_years == Decimal("91.11")
        assert growth.ten_years == Decimal("662.93")
        
        # Test get_growth method
        assert growth.get_growth("1y") == Decimal("-7.52")
        assert growth.get_growth("2y") == Decimal("6.14")
        assert growth.get_growth("3y") == Decimal("25.48")
        assert growth.get_growth("5y") == Decimal("91.11")
        assert growth.get_growth("10y") == Decimal("662.93") 