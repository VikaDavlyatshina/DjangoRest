import stripe

from config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name, description=None):
    """Создаёт продукт в Stripe."""
    try:
        product = stripe.Product.create(
            name=name[:100],
            description=description[:500] if description else "Без описания",
        )
        return product
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка Stripe при создании продукта: {e}")


def create_stripe_price(product_id, amount):
    """Создаёт цену в Stripe."""
    if amount <= 0:
        raise ValueError("Сумма должна быть больше нуля")

    try:
        price = stripe.Price.create(
            currency="rub",
            unit_amount=int(amount * 100),
            product=product_id,
        )
        return price
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка Stripe при создании цены: {e}")


def create_stripe_session(price_id, success_url, cancel_url):
    """Создаёт сессию оплаты в Stripe."""
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session
    except stripe.error.StripeError as e:
        raise Exception(f"Ошибка Stripe при создании сессии: {e}")
