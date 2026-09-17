import unittest

from analytics import cagr, estimate_intrinsic_value, score_company


class AnalyticsTests(unittest.TestCase):
    def test_cagr(self):
        self.assertAlmostEqual(cagr([100, 110, 121]), 10.0, places=3)

    def test_intrinsic_value_positive(self):
        value = estimate_intrinsic_value(
            [1_000_000_000, 1_100_000_000, 1_200_000_000],
            100_000_000,
            2_000_000_000,
            500_000_000,
            [6, 8, 10],
        )
        self.assertIsNotNone(value)
        self.assertGreater(value, 0)

    def test_strong_company_scores_above_weak_company(self):
        strong = score_company({
            "roe_avg": 22, "roic_avg": 18, "fcf_margin_avg": 18, "debt_to_fcf": 1.2,
            "revenue_cagr": 10, "eps_cagr": 12, "fcf_cagr": 11, "share_change_cagr": -1,
            "positive_fcf_ratio": 1, "positive_income_ratio": 1, "margin_of_safety": 25,
            "pe": 18, "fcf_yield": 6,
        })
        weak = score_company({
            "roe_avg": 5, "roic_avg": 3, "fcf_margin_avg": 1, "debt_to_fcf": 7,
            "revenue_cagr": 0, "eps_cagr": -2, "fcf_cagr": None, "share_change_cagr": 4,
            "positive_fcf_ratio": .4, "positive_income_ratio": .5, "margin_of_safety": -20,
            "pe": 45, "fcf_yield": 1,
        })
        self.assertGreater(strong["buffett_score"], weak["buffett_score"])


if __name__ == "__main__":
    unittest.main()
