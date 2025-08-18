"""Discounted Cash Flow (DCF) valuation models and calculations."""

from decimal import Decimal
from typing import Optional, Tuple
import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DiscountedCashFlow:
    """Discounted Cash Flow valuation model."""

    def __init__(self, ticker, perpetual_growth_rate=0.025, required_return=0.1):
        """Initialize DCF model."""
        self.ticker = ticker
        self.perpetual_growth_rate = Decimal(str(perpetual_growth_rate))
        self.required_return = Decimal(str(required_return))

    def calculate_weighted_average_cost_of_capital(self) -> Optional[Decimal]:
        """Calculate WACC."""
        try:
            info = self.ticker.info
            latest_balance_sheet = self.ticker.balance_sheet.iloc[:, 0]

            market_cap = Decimal(str(info["marketCap"]))
            total_debt = self._get_total_debt(latest_balance_sheet)
            total_value = total_debt + market_cap

            cost_of_debt = self._get_cost_of_debt()
            cost_of_equity = self._get_cost_of_equity()

            cost_of_debt_percent = (total_debt / total_value) * cost_of_debt
            cost_of_equity_percent = (market_cap / total_value) * cost_of_equity
            wacc = cost_of_debt_percent + cost_of_equity_percent

            logger.info(
                f"Ticker: {getattr(self.ticker, 'ticker', 'unknown')} | WACC: {wacc:.6f}"
            )

            return wacc

        except Exception as e:
            logger.error(
                f"WACC calculation failed for {getattr(self.ticker, 'ticker', 'unknown')}: {str(e)}"
            )
            return None

    def _get_total_debt(self, balance_sheet) -> Optional[Decimal]:
        long_term_debt = balance_sheet.get("Long Term Debt")
        current_debt = balance_sheet.get("Current Debt")

        if pd.notna(long_term_debt) and pd.notna(current_debt):
            return Decimal(str(long_term_debt + current_debt))
        else:
            return Decimal(str(balance_sheet.get("Total Debt")))

    def _get_cost_of_debt(self) -> Optional[Decimal]:
        """Get cost of debt for current year first, then previous years if current does has no data."""
        FIN_INTEREST_EXP = "Interest Expense"
        CF_INTEREST_EXP = "Interest Paid Supplemental Data"

        for col in self.ticker.financials.columns:
            current_financial_sheet = self.ticker.financials[col]
            current_balance_sheet = self.ticker.balance_sheet[col]
            current_cash_flow = self.ticker.cash_flow[col]

            if FIN_INTEREST_EXP in current_financial_sheet.index and pd.notna(
                current_financial_sheet[FIN_INTEREST_EXP]
            ):
                interest_expense = current_financial_sheet[FIN_INTEREST_EXP]
            elif CF_INTEREST_EXP in current_cash_flow.index and pd.notna(
                current_cash_flow[CF_INTEREST_EXP]
            ):
                interest_expense = current_cash_flow[CF_INTEREST_EXP]
            else:
                continue

            cost_of_debt_pretax = Decimal(str(interest_expense)) / self._get_total_debt(
                current_balance_sheet
            )
            cost_of_debt = cost_of_debt_pretax * (
                1 - self._get_tax_rate(current_financial_sheet)
            )

            logger.info(f"Cost of debt: {cost_of_debt:.4f}, year: {col}")

            return Decimal(cost_of_debt)

        return None

    def _get_cost_of_equity(self) -> Optional[Decimal]:
        beta = Decimal(str(self.ticker.info.get("beta", 1.0)))

        # Treasury rate
        tnx = yf.Ticker("^TNX")
        treasury_10y = Decimal(str(tnx.history(period="1d").iloc[-1]["Close"] / 100))

        # Cost of Equity = Treasury + Beta * (Required Return - Treasury)
        cost_of_equity = treasury_10y + beta * (self.required_return - treasury_10y)

        return Decimal(str(cost_of_equity))

    def _get_tax_rate(self, financial) -> Optional[Decimal]:
        """Get tax rate"""
        pretax_income = financial.loc["Pretax Income"]
        income_tax_expense = financial.loc["Tax Provision"]
        return Decimal(str(income_tax_expense)) / Decimal(str(pretax_income))


if __name__ == "__main__":
    ticker = yf.Ticker("lulu")
    dcf = DiscountedCashFlow(ticker)
    wacc = dcf.calculate_weighted_average_cost_of_capital()
    print(f"WACC: {wacc}")
