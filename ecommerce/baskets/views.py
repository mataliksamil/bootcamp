from rest_framework import viewsets, mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from baskets.filters import BasketItemFilter, BasketFilter
from baskets.models import BasketItem, Basket
from baskets.serializers import BasketItemSerializer, BasketSerializer, \
    BasketItemDetailedSerializer, BasketDetailedSerializer, BasketItemValidateSerializer
from core.mixins import DetailedViewSetMixin
from baskets.enums import BasketStatus

from pdb import set_trace as bp




class BasketItemViewSet(DetailedViewSetMixin, viewsets.ModelViewSet, ):
    queryset = BasketItem.objects.all()
    serializer_class = BasketItemSerializer
    filterset_class = BasketItemFilter
    serializer_action_classes = {
        "detailed_list": BasketItemDetailedSerializer,
        "detailed": BasketItemDetailedSerializer,
    }


class BasketViewSet(DetailedViewSetMixin, mixins.RetrieveModelMixin,
                    mixins.ListModelMixin, GenericViewSet ):
    http_method_names = ['get',]
    permission_classes = {}
    queryset = Basket.objects.all()
    serializer_class = BasketDetailedSerializer
    filterset_class = BasketFilter
    serializer_action_classes = {
        "list" : BasketDetailedSerializer
    }
    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.user.id
        if user_id:
            queryset = queryset.filter(customer_id=user_id, status= BasketStatus.OPEN)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        user_id = request.user.id
        if not user_id:
            create_serializer = BasketSerializer(
                data= {'customer': None, 'status': BasketStatus.OPEN})
            create_serializer.is_valid(raise_exception=True)
            basket = create_serializer.save()
            serializer = self.get_serializer(basket)
            return Response(serializer.data, status=status.HTTP_200_OK)
        basket = queryset.filter(customer_id=user_id)
        if not basket:
            create_serializer = BasketSerializer(
                data= {'customer': None, 'status': BasketStatus.OPEN})
            create_serializer.is_valid(raise_exception=True)
            basket = create_serializer.save()
            serializer = self.get_serializer(basket)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            serializer = self.get_serializer(basket)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def add_basket_item(self, *args, **kwargs):
        basket = self.get_object()
        add_basket_item_serializer = BasketItemValidateSerializer(data=self.request.data)
        add_basket_item_serializer.is_valid(raise_exception= True)
        product = add_basket_item_serializer.validated_data["product"]
        quantity = add_basket_item_serializer.validated_data["quantity"]
        basket_item = basket.basketitem_set.filter(product_id= product.id).first()
        if quantity > 0:
            if basket_item:
                quantity = quantity + basket_item.quantity
            item_serializer = BasketItemSerializer (instance=basket_item, data={
                "basket":basket.id, "product":product.id, "quantity": quantity,
                "price":product.price.amount})
            item_serializer.is_valid(raise_exception=True)
            item_serializer.save()

        serializer = BasketDetailedSerializer(instance=basket)
        return Response(serializer.data)

    @action(methods=['patch'], detail=True)
    def basket_item(self, *args, **kwargs):
        basket = self.get_object()
        add_basket_item_serializer  = BasketItemValidateSerializer(data=self.request.data)
        add_basket_item_serializer.is_valid(raise_exception=True)
        product = add_basket_item_serializer.validated_data["product"]
        quantity = add_basket_item_serializer.validated_data["quantity"]
        basket_item = basket.basketitem_set.filter(product_id= product.id).first()
        if quantity > 0:
            item_serializer = BasketItemSerializer(instance=basket_item, data={
                "product":product.id, "quantity":quantity, "price": product.price.amount, "basket":basket.id
            })
            item_serializer.is_valid(raise_exception=True)
            item_serializer.save()

        serializer = BasketDetailedSerializer(instance= basket_item)
        return Response(serializer.data)
