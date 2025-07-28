from rest_framework import serializers
from shop.models import (Product,
                         ProductSize,
                         Size,
                         CartItem,
                         Order)


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']


class ProductSizeSerializer(serializers.ModelSerializer):
    size = SizeSerializer()

    class Meta:
        model = ProductSize
        fields = ['id', 'size', 'quantity']


class ProductSerializer(serializers.ModelSerializer):
    product_sizes = ProductSizeSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image', 'product_sizes']

class CartItemSerializer(serializers.Serializer):
    product = ProductSerializer()
    size = SizeSerializer()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'size', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return float(obj.product.price) * obj.quantity


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'total', 'created_at', 'comment']
