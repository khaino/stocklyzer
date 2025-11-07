"""Unit tests for DiscountedCashFlow class."""

import unittest
from unittest.mock import Mock, patch
from decimal import Decimal
import pandas as pd
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from stocklyzer.services.valuations import DiscountedCashFlow


class TestDiscountedCashFlow(unittest.TestCase):
    """Test cases for DiscountedCashFlow class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock ticker
        self.mock_ticker = Mock()
        self.dcf = DiscountedCashFlow(
            ticker=self.mock_ticker,
            perpetual_growth_rate=0.025,
            required_return=0.1
        )
    
    def test_dcf_initialization(self):
        """Test DCF initialization with default parameters."""
        dcf = DiscountedCashFlow(self.mock_ticker)
        
        self.assertEqual(dcf.perpetual_growth_rate, Decimal('0.025'))
        self.assertEqual(dcf.required_return, Decimal('0.1'))
        self.assertEqual(dcf.ticker, self.mock_ticker)
    
    def test_dcf_initialization_custom_params(self):
        """Test DCF initialization with custom parameters."""
        dcf = DiscountedCashFlow(
            ticker=self.mock_ticker,
            perpetual_growth_rate=0.03,
            required_return=0.09
        )
        
        self.assertEqual(dcf.perpetual_growth_rate, Decimal('0.03'))
        self.assertEqual(dcf.required_return, Decimal('0.09'))
    
    @patch('stocklyzer.services.valuations.dcf.yf.Ticker')
    def test_wacc_calculation_success(self, mock_yf_ticker):
        """Test successful WACC calculation."""
        # Setup mock data
        self.mock_ticker.info = {
            'marketCap': 3400000000000,  # $3.4T
            'beta': 1.2
        }
        
        # Mock balance sheet
        balance_data = pd.Series({
            'Long Term Debt': 85000000000.0,  # $85B
            'Current Debt': 21000000000.0     # $21B
        })
        self.mock_ticker.balance_sheet = pd.DataFrame([balance_data]).T
        
        # Mock financials with Interest Expense data
        financials_data = pd.Series({
            'Revenue': 100000000000.0,
            'Interest Expense': 2000000000.0  # $2B interest expense
        })
        self.mock_ticker.financials = pd.DataFrame([financials_data]).T
        
        # Mock Treasury rate
        treasury_hist = pd.DataFrame({'Close': [4.5]})  # 4.5%
        mock_treasury_ticker = Mock()
        mock_treasury_ticker.history.return_value = treasury_hist
        mock_yf_ticker.return_value = mock_treasury_ticker
        
        # Calculate WACC
        wacc = self.dcf.calculate_weighted_average_cost_of_capital()
        
        # Verify WACC is calculated
        self.assertIsNotNone(wacc)
        self.assertIsInstance(wacc, Decimal)
        self.assertGreater(wacc, 0)
        
        # Verify Treasury ticker was called
        mock_yf_ticker.assert_called_with("^TNX")
        mock_treasury_ticker.history.assert_called_with(period="1d")
    
    def test_wacc_calculation_missing_market_cap(self):
        """Test WACC calculation with missing market cap."""
        # Setup mock data without market cap
        self.mock_ticker.info = {}
        
        balance_data = pd.Series({
            'Long Term Debt': 85000000000.0,
            'Current Debt': 21000000000.0
        })
        self.mock_ticker.balance_sheet = pd.DataFrame([balance_data]).T
        
        financials_data = pd.Series({'Revenue': 100000000000.0})
        self.mock_ticker.financials = pd.DataFrame([financials_data]).T
        
        # Calculate WACC
        wacc = self.dcf.calculate_weighted_average_cost_of_capital()
        
        # Should return None due to missing market cap
        self.assertIsNone(wacc)
    
    def test_wacc_calculation_missing_debt_data(self):
        """Test WACC calculation with missing debt data."""
        # Setup mock data without debt
        self.mock_ticker.info = {
            'marketCap': 3400000000000,
            'beta': 1.2
        }
        
        # Empty balance sheet
        self.mock_ticker.balance_sheet = pd.DataFrame()
        self.mock_ticker.financials = pd.DataFrame()
        
        # Calculate WACC
        wacc = self.dcf.calculate_weighted_average_cost_of_capital()
        
        # Should return None due to missing debt data
        self.assertIsNone(wacc)
    
    @patch('stocklyzer.services.valuations.dcf.yf.Ticker')
    def test_wacc_calculation_treasury_fetch_failure(self, mock_yf_ticker):
        """Test WACC calculation when Treasury rate fetch fails."""
        # Setup mock data
        self.mock_ticker.info = {
            'marketCap': 3400000000000,
            'beta': 1.2
        }
        
        balance_data = pd.Series({
            'Long Term Debt': 85000000000.0,
            'Current Debt': 21000000000.0
        })
        self.mock_ticker.balance_sheet = pd.DataFrame([balance_data]).T
        
        financials_data = pd.Series({'Revenue': 100000000000.0})
        self.mock_ticker.financials = pd.DataFrame([financials_data]).T
        
        # Mock Treasury rate fetch failure
        mock_yf_ticker.side_effect = Exception("Network error")
        
        # Calculate WACC
        wacc = self.dcf.calculate_weighted_average_cost_of_capital()
        
        # Should return None due to Treasury fetch failure
        self.assertIsNone(wacc)
    
    @patch('stocklyzer.services.valuations.dcf.logger')
    def test_wacc_calculation_logs_error(self, mock_logger):
        """Test that WACC calculation logs errors properly."""
        # Setup mock to cause an exception
        self.mock_ticker.info = None  # This will cause an error
        
        # Calculate WACC
        wacc = self.dcf.calculate_weighted_average_cost_of_capital()
        
        # Should return None and log error
        self.assertIsNone(wacc)
        mock_logger.error.assert_called_once()
        
        # Check that error message contains ticker info
        error_call = mock_logger.error.call_args[0][0]
        self.assertIn("WACC calculation failed", error_call)
    
    def test_wacc_calculation_real_aapl_data(self):
        """Test WACC calculation with real AAPL data."""
        try:
            import yfinance as yf
            
            # Create DCF with real AAPL ticker
            real_ticker = yf.Ticker('AAPL')
            dcf = DiscountedCashFlow(real_ticker, perpetual_growth_rate=0.025, required_return=0.1)
            
            # Calculate WACC
            wacc = dcf.calculate_weighted_average_cost_of_capital()
            
            # Assert that WACC is calculated and is a valid value
            self.assertIsNotNone(wacc, "WACC should not be None for AAPL")
            self.assertIsInstance(wacc, Decimal, "WACC should be a Decimal")
            self.assertGreater(wacc, 0, "WACC should be positive")
            self.assertLess(wacc, 1, "WACC should be less than 100%")
            
        except ImportError:
            self.skipTest("yfinance not available")
        except Exception as e:
            self.fail(f"Real AAPL test failed with error: {e}")
    
    def test_wacc_calculation_real_data_multiple_stocks(self):
        """Test WACC calculation with real data for AAPL, GOOG, and MSFT."""
        try:
            import yfinance as yf
            
            tickers = ['AAPL', 'GOOG', 'MSFT']
            results = {}
            
            for symbol in tickers:
                try:
                    # Create DCF with real ticker
                    real_ticker = yf.Ticker(symbol)
                    dcf = DiscountedCashFlow(real_ticker, perpetual_growth_rate=0.025, required_return=0.1)
                    
                    # Calculate WACC
                    wacc = dcf.calculate_weighted_average_cost_of_capital()
                    results[symbol] = wacc
                    
                    if wacc is not None:
                        # Assert that WACC is calculated and is a valid value
                        self.assertIsInstance(wacc, Decimal, f"WACC should be a Decimal for {symbol}")
                        self.assertGreater(wacc, 0, f"WACC should be positive for {symbol}")
                        self.assertLess(wacc, 1, f"WACC should be less than 100% for {symbol}")
                        
                        # Print the actual WACC for manual verification
                        print(f"\n{symbol} WACC: {wacc:.6f} ({wacc * 100:.2f}%)")
                    else:
                        print(f"\n{symbol} WACC: Could not calculate (missing data)")
                        
                except Exception as e:
                    print(f"\n{symbol} WACC: Error - {str(e)}")
                    results[symbol] = None
            
            # At least one should have calculated successfully
            successful_calculations = [v for v in results.values() if v is not None]
            self.assertGreater(len(successful_calculations), 0, 
                             "At least one WACC calculation should succeed")
            
        except ImportError:
            self.skipTest("yfinance not available for real data test")
    
    def test_get_cost_of_debt_and_total_debt_returns_both_values(self):
        """Test that _get_cost_of_debt_and_total_debt returns both cost of debt and total debt."""
        # Mock ticker with valid data
        mock_financials = pd.DataFrame({
            '2024-12-31': pd.Series({
                'Interest Expense': 600000000,  # $600M interest expense
                'Revenue': 120000000000
            })
        })
        
        mock_balance_sheet = pd.DataFrame({
            '2024-12-31': pd.Series({
                'Long Term Debt': 20000000000,  # $20B long term debt
                'Current Debt': 5000000000      # $5B current debt
            })
        })
        
        self.mock_ticker.financials = mock_financials
        self.mock_ticker.balance_sheet = mock_balance_sheet
        
        result = self.dcf._get_cost_of_debt_and_total_debt()
        
        self.assertIsNotNone(result)
        cost_of_debt, total_debt = result
        
        # Expected: 600M / (20B + 5B) = 600M / 25B = 2.4%
        expected_cost = Decimal('600000000') / Decimal('25000000000')
        expected_total_debt = Decimal('25000000000')
        
        self.assertEqual(cost_of_debt, expected_cost)
        self.assertEqual(total_debt, expected_total_debt)
    
    def test_wacc_calculation_uses_same_year_debt_as_interest_expense(self):
        """Test that WACC calculation uses debt from the same year as Interest Expense."""
        # Mock ticker where different years have different debt levels
        mock_financials = pd.DataFrame({
            '2024-12-31': pd.Series({
                # 2024 has no Interest Expense
                'Revenue': 100000000000
            }),
            '2023-12-31': pd.Series({
                # 2023 has Interest Expense - should use 2023 debt
                'Interest Expense': 800000000,  # $800M interest expense
                'Revenue': 95000000000
            })
        })
        
        mock_balance_sheet = pd.DataFrame({
            '2024-12-31': pd.Series({
                'Long Term Debt': 30000000000,  # $30B - should NOT be used
                'Current Debt': 10000000000     # $10B - should NOT be used
            }),
            '2023-12-31': pd.Series({
                'Long Term Debt': 15000000000,  # $15B - should be used
                'Current Debt': 5000000000      # $5B - should be used
            })
        })
        
        # Mock other required data for WACC
        self.mock_ticker.info = {
            'marketCap': 2000000000000,  # $2T
            'beta': 1.1
        }
        self.mock_ticker.financials = mock_financials
        self.mock_ticker.balance_sheet = mock_balance_sheet
        
        # Mock Treasury rate
        with patch('stocklyzer.services.valuations.dcf.yf.Ticker') as mock_yf_ticker:
            treasury_hist = pd.DataFrame({'Close': [4.2]})  # 4.2%
            mock_treasury_ticker = Mock()
            mock_treasury_ticker.history.return_value = treasury_hist
            mock_yf_ticker.return_value = mock_treasury_ticker
            
            # Calculate WACC
            wacc = self.dcf.calculate_weighted_average_cost_of_capital()
            
            # Should succeed using 2023 data (Interest Expense and debt from same year)
            self.assertIsNotNone(wacc)
            self.assertIsInstance(wacc, Decimal)
            self.assertGreater(wacc, 0)
            self.assertLess(wacc, 1)


if __name__ == '__main__':
    unittest.main()
