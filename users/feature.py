# class PaymentStatusView(APIView):
#     """
#     Проверка статуса оплаты
#     GET /api/users/payments/status/<session_id>/
#     """
#
#     def get(self, request, session_id):
#         # Находим платёж по session_id
#         payment = get_object_or_404(
#             Payments,
#             stripe_session_id=session_id,
#             user=request.user
#         )
#
#         # Если уже оплачено в системе - возвращаем сразу
#         if payment.is_paid:
#             return Response({
#                 'payment_id': payment.id,
#                 'is_paid': True,
#                 'status': 'paid',
#                 'amount': payment.payment_amount,
#                 'course': payment.paid_course.title if payment.paid_course else None
#             })
#
#         # Проверяем в Stripe
#         try:
#             session = stripe.checkout.Session.retrieve(session_id)
#
#             if session.payment_status == 'paid':
#                 payment.is_paid = True
#                 payment.save()
#
#             return Response({
#                 'payment_id': payment.id,
#                 'is_paid': payment.is_paid,
#                 'stripe_status': session.payment_status,
#                 'amount': payment.payment_amount,
#                 'payment_url': payment.payment_url
#             })
#
#         except stripe.error.StripeError as e:
#             return Response(
#                 {'error': str(e)},
#                 status=400
#             )
