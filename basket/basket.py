from decimal import Decimal
from store.models import Product


class Basket:

    def __init__(self, request):

        self.session = request.session

        basket = self.session.get('skey')

        if basket is None:
            basket = self.session['skey'] = {}

        self.basket = basket


    def add(self, product, qty):

        product_id = str(product.id)

        if product_id not in self.basket:

            self.basket[product_id] = {
                'price': str(product.price),
                'qty': qty
            }

        else:

            self.basket[product_id]['qty'] = qty

        self.session.modified = True


    def __len__(self):

        return sum(item['qty'] for item in self.basket.values())


    def get_subtotal(self):
        subtotal = sum(
            Decimal(item['price']) * item['qty']
            for item in self.basket.values()
        )
        return Decimal(subtotal).quantize(Decimal('0.01')) if subtotal else Decimal('0.00')

    def get_tax(self):
        subtotal = self.get_subtotal()
        if subtotal == Decimal('0.00'):
            return Decimal('0.00')
        return (subtotal * Decimal('0.10')).quantize(Decimal('0.01'))

    def get_shipping_price(self):
        if len(self) == 0 or self.get_subtotal() == Decimal('0.00'):
            return Decimal('0.00')
        return Decimal('200.00')

    def get_total_price(self):
        if len(self) == 0 or self.get_subtotal() == Decimal('0.00'):
            return Decimal('0.00')
        total = self.get_subtotal() + self.get_tax() + self.get_shipping_price()
        return total.quantize(Decimal('0.01'))

    def get_items_data(self):
        product_ids = self.basket.keys()
        products = Product.objects.filter(id__in=product_ids)
        prod_map = {str(p.id): p for p in products}
        items = []
        for pid, item in self.basket.items():
            prod = prod_map.get(pid)
            if prod:
                first_image = prod.images.first()
                image_url = first_image.image.url if first_image else ""
                items.append({
                    'id': pid,
                    'title': prod.title,
                    'price': str(item['price']),
                    'qty': item['qty'],
                    'total_price': str(Decimal(item['price']) * item['qty']),
                    'image': image_url
                })
        return items

    def __iter__(self):

        product_ids = self.basket.keys()

        products = Product.objects.filter(id__in=product_ids)

        basket = self.basket.copy()

        for product in products:
            basket[str(product.id)]['product'] = product

        for item in basket.values():

            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['qty']

            yield item

    def update(self, product_id, qty):

        product_id = str(product_id)

        if product_id in self.basket:
            if qty > 0:
                self.basket[product_id]['qty'] = qty
            else:
                del self.basket[product_id]

            self.session.modified = True

    def delete(self, product_id):

        product_id = str(product_id)

        if product_id in self.basket:
            del self.basket[product_id]
            self.session.modified = True        