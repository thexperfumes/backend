from num2words import num2words
from decimal import Decimal

def amount_to_words(amount: Decimal):
    rupees = int(amount)
    paise = int((amount - rupees) * 100)

    words = num2words(rupees, lang="en_IN").replace(",", "").title()
    text = f"Indian Rupees {words}"

    if paise > 0:
        text += f" And {num2words(paise).title()} Paise"

    return text + " Only"
