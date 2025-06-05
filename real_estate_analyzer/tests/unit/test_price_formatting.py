#!/usr/bin/env python3
"""
Test script to demonstrate price formatting improvements for sliders.
This shows the current formatting and potential improvements for K/M notation.
"""

from src.utils.formatters import NumberFormatter
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_current_price_formatting():
    """Test the current price formatting functionality."""
    print("🔢 Current Price Formatting Examples\n")
    print("=" * 50)

    # Test various price values
    test_prices = [
        150000,     # 150K
        500000,     # 500K
        1000000,    # 1M
        1350000,    # 1.35M
        1500000,    # 1.5M
        2000000,    # 2M
        2500000,    # 2.5M
        5000000,    # 5M
        10000000,   # 10M
    ]

    print("Value\t\tShort Form\t\tLong Form")
    print("-" * 50)

    for price in test_prices:
        short = NumberFormatter.format_currency(price, short_form=True)
        long = NumberFormatter.format_currency(price, short_form=False)
        print(f"{price:,}\t\t{short}\t\t\t{long}")

    print("\n" + "=" * 50)


def test_slider_marks_formatting():
    """Test slider marks formatting for different price ranges."""
    print("\n🎚️  Slider Marks Formatting Examples\n")
    print("=" * 50)

    # Test different price ranges
    test_ranges = [
        (150000, 500000, "Small Budget Range"),
        (1000000, 2000000, "Medium Budget Range"),
        (1500000, 3000000, "Large Budget Range"),
        (3000000, 10000000, "Premium Range")
    ]

    for min_price, max_price, description in test_ranges:
        print(f"\n{description}: ₪{min_price:,} - ₪{max_price:,}")
        print("Current slider marks:")

        marks = NumberFormatter.create_price_marks(
            min_price, max_price, num_marks=5)
        for value, label in marks.items():
            print(f"  {value:,} → {label}")


def test_enhanced_formatting():
    """Test enhanced formatting with different decimal precision."""
    print("\n✨ Enhanced Formatting Options\n")
    print("=" * 50)

    test_prices = [1350000, 1750000, 2250000]

    print("Value\t\tDefault\t\t1 Decimal\t2 Decimals")
    print("-" * 60)

    for price in test_prices:
        default = NumberFormatter.format_currency(
            price, short_form=True, decimals=0)
        one_decimal = NumberFormatter.format_currency(
            price, short_form=True, decimals=1)
        two_decimals = NumberFormatter.format_currency(
            price, short_form=True, decimals=2)
        print(f"{price:,}\t\t{default}\t\t{one_decimal}\t\t{two_decimals}")


def demonstrate_tooltip_format():
    """Demonstrate how tooltip formatting could work."""
    print("\n🛠️  Tooltip Formatting Demonstration\n")
    print("=" * 50)

    print("Current Dash RangeSlider tooltips show raw values:")
    print("  Example: When slider value is 1350000, tooltip shows '1350000'")
    print("\nWith K/M formatting, tooltips could show:")
    print("  Example: When slider value is 1350000, tooltip shows '₪1.35M'")

    print("\nCurrent implementation:")
    print("  - Slider marks: Already use K/M format ✅")
    print("  - Tooltips: Show raw numbers (could be improved)")

    print("\nFormatter examples for common values:")
    common_values = [250000, 750000, 1250000, 1750000, 2500000]

    for value in common_values:
        formatted = NumberFormatter.format_currency(
            value, short_form=True, decimals=1)
        print(f"  {value:,} → {formatted}")


def show_current_vs_improved():
    """Show comparison between current and potential improved formatting."""
    print("\n🔄 Current vs Improved Formatting\n")
    print("=" * 50)

    # Simulate slider marks for a typical price range
    min_price, max_price = 1000000, 3000000
    marks = NumberFormatter.create_price_marks(
        min_price, max_price, num_marks=5)

    print("CURRENT IMPLEMENTATION:")
    print("✅ Slider marks already use K/M format:")
    for value, label in marks.items():
        print(f"   {label}")

    print("\n✅ The current formatting is already optimized!")
    print("   - Uses ₪1M instead of ₪1,000,000")
    print("   - Uses ₪1.5M for values like ₪1,500,000")
    print("   - Automatically chooses best format based on value")

    print("\nPOSSIBLE IMPROVEMENTS:")
    print("1. Tooltip formatting (requires custom JS or Dash component)")
    print("2. Input field placeholder formatting (already implemented)")
    print("3. More decimal precision for mid-range values")


def main():
    """Run all formatting tests and demonstrations."""
    print("💰 Price Formatting Analysis for Yad2 Real Estate Dashboard")
    print("=" * 60)

    test_current_price_formatting()
    test_slider_marks_formatting()
    test_enhanced_formatting()
    demonstrate_tooltip_format()
    show_current_vs_improved()

    print("\n" + "=" * 60)
    print("📋 SUMMARY:")
    print("✅ Current slider marks already use K/M formatting")
    print("✅ NumberFormatter.format_currency() supports short_form=True")
    print("✅ Price ranges automatically show ₪1.5M instead of ₪1,500,000")
    print("ℹ️  Tooltips show raw values (this is a Dash limitation)")
    print("ℹ️  For better tooltip formatting, would need custom JavaScript")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
